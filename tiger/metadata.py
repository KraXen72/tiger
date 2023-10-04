import json
import os
from collections import Counter
from os.path import abspath
from typing import Any

import eyed3 as tagger
from eyed3.id3 import ID3_V2_3
from eyed3.id3.frames import ImageFrame

import tiger.constants as c
from tiger.extractors import soundcloud_extractor, youtube_extractor
from tiger.utils import clean_title, format_release_date, md_template, sanitize_text, user_picks_tag

# this file parses the extract_info object provided by yt_dlp for informations
# grabs as much info as it can from all over the place: yt music tags, channel name, video title, description and other fields
# puts all of these strings into an array, count how many times each value occurs and the one that occurs most is the most likely result

def get_most_likely_tag(list_of_keys, obj, additional_values = []):
	"""counts how many times each value occurs and returns the value that occurs the most"""

	if "title" in list_of_keys:
		for item in list_of_keys:
			if item in obj:
				obj[item] = clean_title(obj[item])

	tags = [*additional_values]
	for item in list_of_keys:
		if item in obj:
			tags.append(obj[item])

	# stringify the dict into json so Counter doesen't freak out
	for i, tag in enumerate(tags):
		if isinstance(tag, dict):
			tags[i] = json.dumps(tag, separators=(",", ":"))
		if isinstance(tag, int):
			tags[i] = str(tag)

	# filter out none and 'null'
	cleaned_tags = list(filter(lambda x: x is not None and x != "null", tags))

	counts = Counter(cleaned_tags) # count how many times a string occurs in the tags list
	counts_entries = list(counts.items())
	sorted_counts = sorted(counts_entries, key = lambda x: x[1]) # sort it (ascending)
	descending_counts = list(reversed(sorted_counts)) # reverse (descending)

	dehashed_counts = [] # re-parse jsons
	for count_tuple in descending_counts:
		val = count_tuple[0]
		count = count_tuple[1]

		if val.startswith("{") and val.endswith("}"):
			try:
				obj = json.loads(val)
				dehashed_counts.append((obj, count))
			except:
				dehashed_counts.append(count_tuple)
		else:
			dehashed_counts.append(count_tuple)

	top_result = dehashed_counts[0][0]

	# resolve conficlics
	if len(dehashed_counts) > 1 and dehashed_counts[0][1] == dehashed_counts[1][1]:
		second_result = dehashed_counts[1][0]
		# print("top 2 tags have the same count:", dehashed_counts)

		# for example if years look like this: [('2017', 1), ({'year': '2017', 'month': '10', 'day': '19'}, 1)]
		if isinstance(top_result, str) and isinstance(second_result, dict):
			top_result, second_result = second_result, top_result

	return top_result, cleaned_tags

def smart_metadata(info):
	"""
	grabs as much info as it can from all over the place
	gets the most likely tag and returns a dict
	"""
	# metadata we care about:
	# title
	# artist
	# album_artist
	# album
	# year
	# genre (inputted by user cause no way of telling)

	# additional
	# publisher (record label)

	md = {}
	md_keys = md_template.copy() # keys to check from the 'info object'. site specific.
	add_values = md_template.copy()
	others = md_template.copy()

	domain = info["webpage_url_domain"]
	# TODO extract this
	match domain:
		case "soundcloud.com":
			md_keys = {
				"title": ["title", "fulltitle"],
				"artist": ["uploader"],
				"album_artist": ["uploader"],
				"album": [], # soundcloud doesen't expose album metadata?
				"year": ["upload_date"],
				"publisher": []
			}
			add_values = soundcloud_extractor(info)
		case _:
			if domain != "youtube.com":
				print("[warning] unsupported domain:", domain, "using youtube extractor as fallback.")
			md_keys = {
				"title": ["title", "track", "alt_title"],
				"artist": ["artist", "channel", "creator"],
				"album_artist": [],
				"album": ["album"],
				"year": ["release_date", "release_year"],
				"publisher": []
			}
			add_values = youtube_extractor(info)

	# pass all the vales to get_most_likely_tag
	# which counts how many times each value occurs and returns the value that occurs the most
	# also dumps all the other possibilities into the other dictionary

	md["title"], others["title"] =                  get_most_likely_tag(md_keys["title"], info, add_values["title"])
	md["artist"], others["artist"] =                get_most_likely_tag(md_keys["artist"], info, add_values["artist"])
	md["album_artist"], others["album_artist"] =    get_most_likely_tag(md_keys["album_artist"], info, [md["artist"]] + add_values["album_artist"])

	# fallback: title (Single) => album, only if there is no album yet
	if ("album" not in info) and len(add_values["album"]) == 0:
		add_values["album"].append(f"{md['title']} (Single)")

	md["album"], others["album"] =                  get_most_likely_tag(md_keys["album"], info, add_values["album"])
	md["year"], others["year"] =                    get_most_likely_tag(md_keys["year"], info, add_values["year"])

	if isinstance(md["year"], str):
		md["year"] = { "year": md["year"] }

	if len(add_values["publisher"]) == 0: # publishe from album_artist, only if there is no publisher yet
		add_values["publisher"].append(md["album_artist"])

	md["publisher"], others["publisher"] =          get_most_likely_tag(md_keys["publisher"], info, add_values["publisher"])

	# fix ups
	if md["publisher"] == f"{md['year']['year']} {md['artist']}":
		md["publisher"] = md["artist"]

	# print(others)
	return md

def interactive_tag_applier(filepath: str, info: dict[str, Any], config):
	# TODO OPUS tag applying support. refactor mp3 tagger and OPUS tagger to an abstraction
	song = tagger.load(filepath)
	song.initTag(version=ID3_V2_3) # init tag with v2.3

	# initalize metadata object with smart metadata
	md = smart_metadata(info)

	title = user_picks_tag("[Title]", md["title"])
	song.tag.title = title

	artist = user_picks_tag("[Artist]", md["artist"])
	song.tag.artist = artist

	final_filename_path = abspath(os.path.join(config["savedir"], f"{sanitize_text(artist)} - {sanitize_text(title)}.mp3"))
	if os.path.exists(final_filename_path):
		print("The songs you're downloading already exists.")
		print("Continue with tagging & overwrite file? Type A to abort, anything else to continue.")
		_overwrite = input("A/*: ")
		if _overwrite == "A":
			quit()

	album_artist = user_picks_tag("[Album artist]", md["album_artist"])
	song.tag.album_artist = album_artist

	album = user_picks_tag("[Album]", md["album"])
	song.tag.album = album

	genre = input("[Genre]: > ")
	if genre != "":
		song.tag.genre = genre

	publisher = user_picks_tag("[Publisher]", md["publisher"])
	if publisher != "":
		song.tag.publisher = publisher

	# upload date usually corresponds to release date even for music-type videos
	rel_date = user_picks_tag("[Release Date]", format_release_date(md["year"], config["current_id3v"]))
	song.tag.release_date = rel_date # this should set TORY when tag version is id3v2.3
	song.tag.original_release_date = rel_date
	song.tag.original_year = rel_date
	song.tag.recording_date = rel_date # the actual year tag

	song.tag.track_num = user_picks_tag("[Track No #]", (1, 1))

	# add the album cover
	# God bless https://stackoverflow.com/questions/38510694/how-to-add-album-art-to-mp3-file-using-python-3#39316853
	song.tag.images.set(ImageFrame.FRONT_COVER, open(c.MUSICDL_ASSETS + "/" + "out.jpg","rb").read(), "image/jpeg")

	song.tag.save(version=config["current_id3v"]) # save tag to song. id3v2.3 is safer
	os.rename(filepath, final_filename_path) # use abspath here to respect savedir


if __name__=="__main__":
	f = open(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "musicdl_assets", "jsondump.json")), "r", encoding="utf8")
	obj = json.load(f)
	f.close()

	result = smart_metadata(obj)
	print(result)