import json
from typing import Any

from yt_dlp import YoutubeDL

import tiger.constants as c

# you can use https://greasyfork.org/en/scripts/446275-youtube-screenshoter to get any frame of the video quickly (hold ctrl to download instead of clipboard)

ASSET_DIR = "musicdl_assets"

def fetch_video_info(link: str, ytd_opts: dict[str, Any], save_json_dump = False):
	ytd_opts = ytd_opts.copy()
	ytd_opts["noprogress"] = True
	ytd_opts["quiet"] = True
	
	ydl = YoutubeDL(ytd_opts)
	prefetch_info = ydl.extract_info(link, download=False)
	if save_json_dump:
		f = open(c.JSONDUMP_PATH, "w", encoding="utf8")
		json.dump(ydl.sanitize_info(prefetch_info), f, indent=4, ensure_ascii=False)
		f.close()

	return prefetch_info

def download_video(link: str, ytd_opts: dict[str, Any]):
	ydl = YoutubeDL(ytd_opts)
	# 1: DOWNLOAD SONG(S)
	info = ydl.extract_info(link, download=True)

	return info
