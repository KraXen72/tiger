import os
import sys
from os.path import abspath

from eyed3.id3 import ID3_V2_3

import tiger.constants as c
from tiger.dl import download_video, fetch_video_info
from tiger.logo import print_logo
from tiger.metadata import interactive_tag_applier
from tiger.thumbnail import ensure_thumbnail_exists, thumb_gui_crop
from tiger.utils import check_title_dirty, load_config

config = {
	"current_id3v": ID3_V2_3,
	"current_format": "mp3",
	"savedir": "D:/music/#deezloader downloads",
	"save_json_dump": True
	# downloading_playlist = False
}

ytd_opts = {
	#"ffmpeg_location": "D:/coding/yt-dlp/ffmpeg-master-latest-win64-gpl-shared/bin/ffmpeg.exe",
	"force-overwrites": True,
	"audio_quality": 0,
	"format": "mp3/bestaudio/best",
	# See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
	"postprocessors": [{  # Extract audio using ffmpeg
		"key": "FFmpegExtractAudio",
		"preferredcodec": "mp3",
	}],
	"test": False
}

def _no_traceback_excepthook(exc_type, exc_val, traceback):
	pass

def main_cli():
	global config
	global ytd_opts

	print_logo()
	print("Tiger: youtube music downloader for lazy perfectionists.")
	print()

	config, ytd_opts = load_config(c.CONFIG_PATH, config, ytd_opts)

	ytd_opts["paths"] = {"home": config["savedir"]}

	# link = "https://www.youtube.com/watch?v=YBHxSFI_Q3Q"
	# link = "https://www.youtube.com/watch?v=gLYWLobR248" #jreg
	# link = https://www.youtube.com/watch?v=29KS5pStm4o # happy pill official visualizer

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
		print("Download song or playlist?")
		confirm = input("type 'p' for playlist, anything else for song only:")
		if confirm.lower() == "p":
			print("[info] downloading whole playlist")
			# flag_downloading_playlist = True
		else:
			link = link[:link.index("&list=")] #slice off the index part
			print("[info] downloading song only")

	# if not flag_downloading_playlist:
	prefetch_info = fetch_video_info(link, ytd_opts, config["save_json_dump"])
	dirty_title = check_title_dirty(prefetch_info["title"])

	if dirty_title is not False:
		print(f"[warning] link you entered contains {dirty_title}")
		print("It is recommended to use a music.youtube.com url or (Offical Audio) instead.")
		confirm = input("type Y/y/Yes to continue, anything else to abort: ")
		if confirm.lower() not in ["y", "yes"]:
			quit()

	print()

	# 1. DOWNLOAD ALL AUDIO
	info = download_video(link, ytd_opts)
	
	for item in info["requested_downloads"]:

		# 2. CROP THUMBNAIL
		print("Go to the new Tkinter window to select your thumbnail")
		thumb_fullpath = abspath(os.path.join(c.MUSICDL_ASSETS, f"thumb[{info['id']}].jpg"))
		ensure_thumbnail_exists(thumb_fullpath, info["thumbnail"])
		thumb_gui_crop(thumb_fullpath=thumb_fullpath)

		# 3. tag the file
		# youtube has some extra fields for music-type videos, so we try to offer those, but fallback to the next best thing
		print("Tagging the song:")
		print("You will be asked about some tags, most of them have a default value")
		print("If it looks good, just hit enter")
		print("If you type anything else, it will be used as the new value.")
		interactive_tag_applier(item["filepath"], info, config)

		print("> Done!")
		os.system("pause")

def main():
	try:
		main_cli()
	except KeyboardInterrupt:
		# whatever cleanup code you need here...
		if sys.excepthook is sys.__excepthook__:
			sys.excepthook = _no_traceback_excepthook
		raise

if __name__ == "__main__":
	main()