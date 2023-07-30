import json
from collections import Counter

import src.constants as c

# this file parses the extract_info object provided by yt_dlp for informations
# grabs as much info as it can from all over the place: yt music tags, channel name, video title, description and other fields
# puts all of these strings into an array, count how many times each value occurs and the one that occurs most is the most likely result


# TODO extract genre? soundccloud has it.
md_template = {
	"title": [],
	"artist": [],
	"album_artist": [],
	"album": [],
	"year": [],
	"publisher": []
}

def parse_date(datestring):
	"""
	parses one of 3 date formats: 2020-07-01, 2020 and 20200630.
	otherwise return None
	"""
	if datestring.count("-") == 2: # 2020-07-01
		parts = datestring.split("-")
		return { "year": parts[0], "month": parts[1], "day": parts[2] }
	elif ("-" not in datestring) and ("." not in datestring):
		if len(datestring) == 4: # 2020
			return { "year": datestring }
		elif len(datestring) == 8: # 20200630
			return { "year": datestring[0:4], "month": datestring[4:6], "day": datestring[6:8] }

def dash_split(string, object):
	split_title = string.split(" - ")
	object["artist"].append(split_title[0])
	object["title"].append(split_title[1])
	return object

def get_most_likely_tag(list_of_keys, obj, additional_values = []):
	"""
	counts how many times each value occurs and returns the value that occurs the most
	"""
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

# site extractors
def youtube_extractor(info):
	add_values = md_template.copy()

	# video title is: Artist - Title format
	if info["title"].count(" - ") == 1:
		add_values = dash_split(info["title"], add_values)

	if info["fulltitle"].count(" - ") == 1:
		add_values = dash_split(info["title"], add_values)

	# channel is: Artist - Topic
	if info["uploader"].endswith(" - Topic"):
		clean_uploader = info["uploader"][:-8] #slice off last 8 ( - Topic)
		if ("categories" not in info) or (info["categories"] == ["Music"]):
			add_values["artist"].append(clean_uploader)

			# parse and use auto-generated description
			if info["description"].endswith("Auto-generated by YouTube."):
				lines = info["description"].split("\n\n")

				if lines[1].count(" · ") == 1: # artist · title
					l1split = lines[1].split(" · ")
					add_values["artist"].append(l1split[1])
					add_values["title"].append(l1split[0])

				add_values["album"].append(lines[2])
				add_values["publisher"].append(lines[3].replace("℗ ", "").replace("℗", ""))

				if lines[4].startswith("Released on: "):
					raw_date = lines[4][13:]
					date = parse_date(raw_date)
					add_values["year"].append(date)

	# fallback: upload date => year, only if there is no date yet
	if ("upload_date" in info) and len(add_values["publisher"]) == 0:
		add_values["year"].append(parse_date(info["upload_date"]))

	return add_values

def soundcloud_extractor(info):
	add_values = md_template.copy()

	add_values["publisher"] = f"{info['uploader']} via SoundCloud."
	# TODO finish soundcloud extractor
	return add_values


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
	md_template.copy() # keys to check from the 'info object'. site specific.
	add_values = md_template.copy()
	others = md_template.copy()

	domain = info["webpage_url_domain"]
	match domain:
		case "soundcloud.com":
			add_values = soundcloud_extractor(info)
		case _:
			if domain != "youtube.com":
				print("[warning] unsupported domain:", domain, "using youtube extractor as fallback.")
			add_values = youtube_extractor(info)
			# TODO finish this

	# pass all the vales to get_most_likely_tag
	# which counts how many times each value occurs and returns the value that occurs the most
	# also dumps all the other possibilities into the other dictionary

	md["title"], others["title"] =                  get_most_likely_tag(["title", "track", "alt_title"], info, add_values["title"])
	md["artist"], others["artist"] =                get_most_likely_tag(["artist", "channel", "creator"], info, add_values["artist"])
	md["album_artist"], others["album_artist"] =    get_most_likely_tag([], info, [md["artist"]] + add_values["album_artist"])

	# fallback: title (Single) => album, only if there is no album yet
	if ("album" not in info) and len(add_values["album"]) == 0:
		add_values["album"].append(f"{md['title']} (Single)")

	md["album"], others["album"] =                  get_most_likely_tag(["album"], info, add_values["album"])
	md["year"], others["year"] =                    get_most_likely_tag(["release_date", "release_year"], info, add_values["year"])

	if type(md["year"]) is str:
		md["year"] = { "year": md["year"] }

	if len(add_values["publisher"]) == 0: # publishe from album_artist, only if there is no publisher yet
		add_values["publisher"].append(md["album_artist"])

	md["publisher"], others["publisher"] =          get_most_likely_tag([], info, add_values["publisher"])

	# fix ups
	if md["publisher"] == f"{md['year']['year']} {md['artist']}":
		md["publisher"] = md["artist"]

	# print(others)
	return md

if __name__=="__main__":
	f = open(c.JSONDUMP_PATH, "r", encoding="utf8")
	obj = json.load(f)
	f.close()

	result = smart_metadata(obj)
	print(result)