import json
import os
from os.path import abspath

from yt_dlp import YoutubeDL # for downloading the song     DOCS: https://github.com/yt-dlp/yt-dlp
from tinytag import TinyTag # for checking bitrate          DOCS: https://github.com/devsnd/tinytag
from ffmpy import FFmpeg # for re-encoding                  DOCS: https://ffmpy.readthedocs.io/en/latest/examples.html
import eyed3 as tagger # for writing tags to the mp3 file   DOCS: https://eyed3.readthedocs.io/en/latest/index.html
from eyed3.id3.frames import ImageFrame
from eyed3.id3 import ID3_V2_3, ID3_V2_4
import urllib.request # for downloading od thumbnail        DOCS: https://docs.python.org/3/library/urllib.request.html#module-urllib.request

from thumblogic import thumb_gui_crop
from smart_metadata import smart_metadata

# you can use https://greasyfork.org/en/scripts/446275-youtube-screenshoter to get any frame of the video quickly (hold ctrl to download instead of clipboard)

# set up urllib. I honestly could've used urllib3 but cba this example was on stackoverflow
opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
urllib.request.install_opener(opener)

def download_image(url, file_path, file_name):
    full_path = file_path + file_name
    urllib.request.urlretrieve(url, full_path)

def sanitizeText(text):
    forbidden = [ "<", ">", ":", '"', "\\", "/", "|", "?", "*", "."]
    for letter in forbidden:
        text = text.replace(letter, "_")
    return text

def user_picks_tag(text, default):
    default_text = "(enter a value)" if default == "" else default
    assemble = "{}: {} > ".format(text, default_text)
    q = input(assemble)
    if q.lower() == "" and default_text != "(enter a value)":
        return default
    else:
        return q

def format_release_date(d, current_id3v):
    if current_id3v == ID3_V2_4:
        return f"{d['year']}-{d['month']}-{d['day']}"
    else:
        return d['year'] # return just the year for id3v2.3

# constants
ASSET_DIR = "musicdl_assets"
CWD = abspath(os.getcwd())
CURRENT_ID3V = ID3_V2_3

savedir = "D:/music/#deezloader downloads"
save_json_dump = True
skip_reencode = True # you can skip reencode if you don't have lame installed

ytd_opts = {
    #"ffmpeg_location": "D:/coding/yt-dlp/ffmpeg-master-latest-win64-gpl-shared/bin/ffmpeg.exe",
    "force-overwrites": True,
    "audio_quality": 0,
    'format': 'mp3/bestaudio/best',
    # ?????? See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
    'postprocessors': [{  # Extract audio using ffmpeg
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
    }],
    "test": False
}

print("""
???????????????????????????  ????????? ???????????????  ?????????????????? ??????????????????  
???  ????????? ????????????????????? ????????? ?????? ??????   ???????????? ??? ?????????
??? ???????????? ?????????????????????????????????????????? ????????????  ????????? ????????? ???
??? ???????????? ??? ????????????????????????  ?????? ?????????  ????????????????????????  
  ???????????? ??? ????????????????????????????????????????????????????????????????????? ????????????
  ??? ??????    ??????  ??????   ??? ????????? ?????? ??? ?????? ????????????
    ???    ??? ??? ??? ???   ??? ??? ??? ???    ?????? ??? ??? 
  ??? ???    ??? ??? ??? ???   ???     ???    ??????   ??? 
           ???       ??? ???   ???     ???     
""")
print("Tiger: youtube music downloader for lazy perfectionists.")
print()

if os.path.exists(abspath(CWD + "/" + "config.json")): 
    f = open("config.json", 'r', encoding='utf8')
    config_obj = json.load(f)
    f.close()

    # apply config options
    if 'savedir' in config_obj:
        savedir = config_obj["savedir"]
    if 'save_json_dump' in config_obj:
        save_json_dump = config_obj["save_json_dump"]
    if 'skip_reencode' in config_obj:
        skip_reencode = config_obj["skip_reencode"]
    if 'ffmpeg_location' in config_obj:
        ytd_opts["ffmpeg_location"] = config_obj["ffmpeg_location"]
    else:
        print("[warning]: no ffmpeg location detected in config. falling back to PATH/system")

    if 'id3v' in config_obj:
        if config_obj['id3v'] == "2.3":
            CURRENT_ID3V = ID3_V2_3
            print("[info] config set the ID3 version to " + config_obj["id3v"])
        if config_obj['id3v'] == "2.4":
            CURRENT_ID3V = ID3_V2_4
            print("[info] config set the ID3 version to " + config_obj["id3v"])

    #print("[success]: Loaded config file 'config.json'.")
else:
    print("[warning]: no 'config.json' file detected. Make sure to create one first (check readme)")
    os.system("pause")
    quit()

ytd_opts["paths"] = {"home": savedir}

id, title, concatfn = "", "", ""

print("[info] music.youtube.com song links are recommended for more accurate metadata")
print()
link = input("Paste link you want to download: ")
# link = "https://www.youtube.com/watch?v=YBHxSFI_Q3Q"
# link = "https://www.youtube.com/watch?v=gLYWLobR248" #jreg
print()

if "music.youtube.com" in link:
    link = link.replace("music.youtube.com", "youtube.com")
    print("[info] downloading from music.youtube.com with more accurate metadata")

if "&t=" in link:
    link = link[:link.index("&t=")]
    print("[info] stripped timestamp from url")

if "&list=" in link:
    print("[Download song or playlist?]")
    opt = input("type 'p' for playlist, anything else (even enter) for song only:")
    if opt == 'p':
        print("[info] downloading whole playlist")
    else:
        link = link[:link.index("&list=")] #slice off the index part
        print('[info] downloading song only')

with YoutubeDL(ytd_opts) as ydl:
    # 1: DOWNLOAD SONG(S)
    info = ydl.extract_info(link, download=True)
    info = ydl.sanitize_info(info)

    if save_json_dump:
        f = open(ASSET_DIR + "/" +"jsondump.json", 'w', encoding='utf8')
        json.dump(info, f, indent=4, ensure_ascii=False)
        f.close()

    id, title = info["id"], info["title"]
    concatfn = f"{title} [{id}].mp3"
    newconcatfn = f"{title} [{id}] [128k].mp3"

    for item in info["requested_downloads"]:
        # 2. RE-ENCODE SONGS INTO 128 / 320 (if neccesary)
        filepath = item["filepath"]
        desired_bitrate = 128.00

        bitrate = float(TinyTag.get(filepath).bitrate)
        if bitrate > desired_bitrate:
            desired_bitrate = 320.00

        if skip_reencode == False:
            inpDir, outDir = {}, {}
            inpDir[filepath] = None
            outDir[newconcatfn] = f"-hide_banner -c:a libmp3lame -b:a {desired_bitrate}k -y"

            ff = FFmpeg(executable=ytd_opts["ffmpeg_location"], inputs=inpDir, outputs = outDir)
            # print(ff.cmd)
            print(f"> re-encoding to {desired_bitrate}k")
            ff.run(stdout=None)
            print("> re-encoding finished")

            os.remove(filepath)
            os.rename(filepath.replace(".mp3", " [128k].mp3"), filepath)

        # 3. SELECT THUMBNAIL
        # thumb_or_frame = input("> Album Art: Use frame from the video or Thumbnail? type f = frame, anything else (including enter) = thumb")
        
        thumb_fullpath = ASSET_DIR + "/" + f"thumb[{id}].jpg"
        if os.path.exists(thumb_fullpath) == False:
            thumb_url = info["thumbnail"].replace("/vi_webp/", "/vi/").replace(".webp", ".jpg")
            download_image(thumb_url, ASSET_DIR + "/", f"thumb[{id}].jpg")
        
        # 4. CALL GUI TO CROP THUMBNAIL
        thumb_fn = f"thumb[{id}].jpg"
        thumb_path = ASSET_DIR + "/" + thumb_fn
        print("Go to the new Tkinter window to select your thumbnail")
        thumb_gui_crop(thumb_fullpath= thumb_path)

        # 5. tag the mp3
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
        rel_date = user_picks_tag("[Release Date]", format_release_date(md['year'], CURRENT_ID3V))
        song.tag.release_date = rel_date # this should set TORY when tag version is id3v2.3
        song.tag.original_release_date = rel_date
        song.tag.original_year = rel_date
        song.tag.recording_date = rel_date # the actual year tag
        
        song.tag.track_num = user_picks_tag("[Track No #]", (1, 1))

        # add the album cover
        # God bless https://stackoverflow.com/questions/38510694/how-to-add-album-art-to-mp3-file-using-python-3#39316853
        song.tag.images.set(ImageFrame.FRONT_COVER, open(ASSET_DIR + "/" + "out.jpg",'rb').read(), 'image/jpeg')
        
        song.tag.save(version=CURRENT_ID3V) # save tag to song. id3v2.3 is safer
        os.rename(filepath, abspath(savedir + "/" + f"{sanitizeText(artist)} - {sanitizeText(title)}.mp3")) # use abspath here to respect savedir

        print("> Done!")
        os.system("pause")


