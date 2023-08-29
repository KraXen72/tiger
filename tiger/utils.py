import urllib.request

from eyed3.id3 import ID3_V2_4

opener = urllib.request.build_opener()
opener.addheaders = [("User-agent", "Mozilla/5.0")]
urllib.request.install_opener(opener)

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