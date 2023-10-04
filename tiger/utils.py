import json
import os
import re
import urllib.request
from typing import Any

from eyed3.id3 import ID3_V2_3, ID3_V2_4

import tiger.constants as c

opener = urllib.request.build_opener()
opener.addheaders = [("User-agent", "Mozilla/5.0")]
urllib.request.install_opener(opener)

dirty_title_pattern = re.compile(r"(?:\(|\[)Official(?:\sMusic)?\s(?:Video|Vi(?:z|s)ualizer)(?:\)|\])", flags=re.IGNORECASE)

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

def download_image(url, result_path):
	urllib.request.urlretrieve(url, result_path)

def sanitize_text(text: str):
	# possibly rewrite as regex?
	forbidden = [ "<", ">", ":", '"', "\\", "/", "|", "?", "*", "."]
	for letter in forbidden:
		text = text.replace(letter, "_")
	return text

def user_picks_tag(text: str, default: str):
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
	
def load_config(config_path: str, default_config: dict[str, Any], default_ytd_opts: dict[str, Any]):
	config = default_config.copy()
	ytd_opts = default_ytd_opts.copy()

	if not os.path.exists(c.CONFIG_PATH):
		print("[warning]: no 'config.json' file detected. Make sure to create one first (check readme)")
		os.system("pause")
		quit()

	f = open(config_path, "r", encoding="utf8")
	config_obj = json.load(f)
	f.close()

	# apply config options
	if "savedir" in config_obj:
		config["savedir"] = config_obj["savedir"]

	if "audio_format" in config_obj and config_obj["audio_format"] == "opus":
		config["current_format"] = "opus"
		ytd_opts["format"] = 'bestaudio[format="opus"]/bestaudio/best'
		ytd_opts["postprocessors"][0] = { "key": "FFmpegExtractAudio" }

	print(f"[info] downloading in format {config['current_format']}")

	if "save_json_dump" in config_obj:
		config["save_json_dump"] = config_obj["save_json_dump"]

	if "ffmpeg_location" in config_obj:
		ytd_opts["ffmpeg_location"] = config_obj["ffmpeg_location"]
	else:
		print("[warning]: no ffmpeg location detected in config. falling back to PATH/system")

	if "id3v" in config_obj:
		if config_obj["id3v"] == "2.3":
			config["current_id3v"] = ID3_V2_3
			print("[info] config set the ID3 version to " + config_obj["id3v"])
		if config_obj["id3v"] == "2.4":
			config["current_id3v"] = ID3_V2_4
			print("[info] config set the ID3 version to " + config_obj["id3v"])

	print("[success]: Loaded config file 'config.json'.")
	return config, ytd_opts

def check_title_dirty(title: str) -> str or False: 
	"""check if video title contains some variation of (Official Video)"""
	matches = dirty_title_pattern.findall(title)
	if len(matches) > 0:
		return matches[0]
	else:
		return False
	
def clean_title(title: str) -> str:
	return str(re.sub(dirty_title_pattern, "", title)).strip()

if __name__ == "__main__":
	print(check_title_dirty("grandson x Moby Rich: Happy Pill [OFFICIAL VISUALIZER]"))