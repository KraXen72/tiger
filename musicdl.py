import json
import os
import urllib.request  # for downloading od thumbnail        DOCS: https://docs.python.org/3/library/urllib.request.html#module-urllib.request
from os.path import abspath

import eyed3 as tagger  # for writing tags to the mp3 file   DOCS: https://eyed3.readthedocs.io/en/latest/index.html
from eyed3.id3 import ID3_V2_3, ID3_V2_4
from eyed3.id3.frames import ImageFrame
from yt_dlp import YoutubeDL  # for downloading the song     DOCS: https://github.com/yt-dlp/yt-dlp

import src.constants as c
from src.metadata import smart_metadata
from src.thumbnail_gui import thumb_gui_crop

# you can use https://greasyfork.org/en/scripts/446275-youtube-screenshoter to get any frame of the video quickly (hold ctrl to download instead of clipboard)

opener = urllib.request.build_opener()
opener.addheaders = [("User-agent", "Mozilla/5.0")]
urllib.request.install_opener(opener)

def download_image(url, result_path):
	urllib.request.urlretrieve(url, result_path)

def sanitize_text(text):
	# possibly rewrite as regex?
	forbidden = [ "<", ">", ":", '"', "\\", "/", "|", "?", "*", "."]
	for letter in forbidden:
		text = text.replace(letter, "_")
	return text

def user_picks_tag(text, default):
	default_text = "(enter a value)" if default == "" else default
	q = input(f"{text}: {default_text} > ")
	if q.lower() == "" and default_text != "(enter a value)":
		return default
	else:
		return q

def format_release_date(d, current_id3v):
	if current_id3v == ID3_V2_4:
		return f"{d['year']}-{d['month']}-{d['day']}"
	else:
		return d["year"] # return just the year for id3v2.3
	
# constants
ASSET_DIR = "musicdl_assets"

savedir = "D:/music/#deezloader downloads"
save_json_dump = True

# TODO the word flag might not be the best. possibly rename? it's more like a global setting.
flag_current_id3v = ID3_V2_3
flag_current_format = "mp3"

ytd_opts = {
	#"ffmpeg_location": "D:/coding/yt-dlp/ffmpeg-master-latest-win64-gpl-shared/bin/ffmpeg.exe",
	"force-overwrites": True,
	"audio_quality": 0,
	"format": "mp3/bestaudio/best",
	# ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
	"postprocessors": [{  # Extract audio using ffmpeg
		"key": "FFmpegExtractAudio",
		"preferredcodec": "mp3",
	}],
	"test": False
}

# TODO move this to a file so CTRL + U + ruff doesen't break it
print("""
▄▄▄█████▓  ██▓ ▄████  ▓█████ ██▀███  
▓  ██▒ ▓▒▒▓██▒ ██▒ ▀█ ▓█   ▀▓██ ▒ ██▒
▒ ▓██░ ▒░▒▒██▒▒██░▄▄▄ ▒███  ▓██ ░▄█ ▒
░ ▓██▓ ░ ░░██░░▓█  ██ ▒▓█  ▄▒██▀▀█▄  
  ▒██▒ ░ ░░██░▒▓███▀▒▒░▒████░██▓ ▒██▒
  ▒ ░░    ░▓  ░▒   ▒ ░░░ ▒░ ░ ▒▓ ░▒▓░
	░    ░ ▒ ░ ░   ░ ░ ░ ░    ░▒ ░ ▒ 
  ░ ░    ░ ▒ ░ ░   ░     ░    ░░   ░ 
           ░       ░ ░   ░     ░     
""")
print("Tiger: youtube music downloader for lazy perfectionists.")
print()

if os.path.exists(c.CONFIG_PATH):
	f = open("config.json", "r", encoding="utf8")
	config_obj = json.load(f)
	f.close()

	# apply config options
	if "savedir" in config_obj:
		savedir = config_obj["savedir"]
	if "audio_format" in config_obj and config_obj["audio_format"] == "opus":
		flag_current_format = "opus"
		ytd_opts["format"] = 'bestaudio[format="opus"]/bestaudio/best'
		ytd_opts["postprocessors"][0] = { "key": "FFmpegExtractAudio" }
	print(f"[info] downloading in format {flag_current_format}")
	if "save_json_dump" in config_obj:
		save_json_dump = config_obj["save_json_dump"]
	if "ffmpeg_location" in config_obj:
		ytd_opts["ffmpeg_location"] = config_obj["ffmpeg_location"]
	else:
		print("[warning]: no ffmpeg location detected in config. falling back to PATH/system")

	if "id3v" in config_obj:
		if config_obj["id3v"] == "2.3":
			flag_current_id3v = ID3_V2_3
			print("[info] config set the ID3 version to " + config_obj["id3v"])
		if config_obj["id3v"] == "2.4":
			flag_current_id3v = ID3_V2_4
			print("[info] config set the ID3 version to " + config_obj["id3v"])

	#print("[success]: Loaded config file 'config.json'.")
else:
	print("[warning]: no 'config.json' file detected. Make sure to create one first (check readme)")
	os.system("pause")
	quit()

ytd_opts["paths"] = {"home": savedir}

id, title, concatfn = "", "", ""
# link = "https://www.youtube.com/watch?v=YBHxSFI_Q3Q"
# link = "https://www.youtube.com/watch?v=gLYWLobR248" #jreg

print("[info] music.youtube.com song links are recommended for more accurate metadata")
print()
link = input("Paste link you want to download: ")

if "music.youtube.com" in link:
	link = link.replace("music.youtube.com", "youtube.com")
	print("[info] downloading from music.youtube.com with more accurate metadata")

if "&t=" in link:
	link = link[:link.index("&t=")]
	print("[info] stripped timestamp from url")

if "&list=" in link:
	print("[Download song or playlist?]")
	opt = input("type 'p' for playlist, anything else (even enter) for song only:")
	if opt == "p":
		print("[info] downloading whole playlist")
	else:
		link = link[:link.index("&list=")] #slice off the index part
		print("[info] downloading song only")

with YoutubeDL(ytd_opts) as ydl:
	prefetch_info = ydl.extract_info(link, download=False)
	if save_json_dump:
		f = open(c.JSONDUMP_PATH, "w", encoding="utf8")
		json.dump(ydl.sanitize_info(prefetch_info), f, indent=4, ensure_ascii=False)
		f.close()

	if "(Official" in prefetch_info["title"] and " Video)" in prefetch_info["title"]:
		print('[warning] link you entered contains "(Official" and "Video)"')
		print("It is recommended to use a music.youtube.com url or (Offical Audio) instead.")
		confirm = input("type Y/y/Yes to continue, anything else to abort: ")
		if confirm.lower() not in ["y", "yes"]:
			quit()
print()

with YoutubeDL(ytd_opts) as ydl:
	# 1: DOWNLOAD SONG(S)
	info = ydl.extract_info(link, download=True)

	id, title = info["id"], info["title"]
	concatfn = f"{title} [{id}].mp3"
	newconcatfn = f"{title} [{id}] [128k].mp3"

	for item in info["requested_downloads"]:
		filepath = item["filepath"]

		# 2. SELECT THUMBNAIL
		# thumb_or_frame = input("> Album Art: Use frame from the video or Thumbnail? type f = frame, anything else (including enter) = thumb")
		
		thumb_fullpath = abspath(os.path.join(c.MUSICDL_ASSETS, f"thumb[{id}].jpg"))
		if os.path.exists(thumb_fullpath) is False:
			thumb_url = info["thumbnail"].replace("/vi_webp/", "/vi/").replace(".webp", ".jpg")
			download_image(thumb_url, thumb_fullpath)

		# 3. CALL GUI TO CROP THUMBNAIL
		print("Go to the new Tkinter window to select your thumbnail")
		thumb_gui_crop(thumb_fullpath=thumb_fullpath)

		# 4. tag the file
		# youtube has some extra fields for music-type videos, so we try to offer those, but fallback to the next best thing
		print("Tagging the song:")
		print("You will be asked about some tags, most of them have a default value")
		print("If it looks good, just hit enter")
		print("If you type anything else, it will be used as the new value.")

		song = tagger.load(filepath)
		song.initTag(version=ID3_V2_3) # init tag with v2.3

		# initalize metadata object with smart metadata
		md = smart_metadata(info)

		title = user_picks_tag("[Title]", md["title"])
		song.tag.title = title

		artist = user_picks_tag("[Artist]", md["artist"])
		song.tag.artist = artist

		final_filename_path = abspath(os.path.join(savedir, f"{sanitize_text(artist)} - {sanitize_text(title)}.mp3"))
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
		rel_date = user_picks_tag("[Release Date]", format_release_date(md["year"], flag_current_id3v))
		song.tag.release_date = rel_date # this should set TORY when tag version is id3v2.3
		song.tag.original_release_date = rel_date
		song.tag.original_year = rel_date
		song.tag.recording_date = rel_date # the actual year tag

		song.tag.track_num = user_picks_tag("[Track No #]", (1, 1))

		# add the album cover
		# God bless https://stackoverflow.com/questions/38510694/how-to-add-album-art-to-mp3-file-using-python-3#39316853
		song.tag.images.set(ImageFrame.FRONT_COVER, open(ASSET_DIR + "/" + "out.jpg","rb").read(), "image/jpeg")

		song.tag.save(version=flag_current_id3v) # save tag to song. id3v2.3 is safer
		os.rename(filepath, final_filename_path) # use abspath here to respect savedir

		print("> Done!")
		os.system("pause")
