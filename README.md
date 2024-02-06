# tiger 
```
  
▄▄▄█████▓  ██▓ ▄████  ▓█████ ██▀███  
▓  ██▒ ▓▒▒▓██▒ ██▒ ▀█ ▓█   ▀▓██ ▒ ██▒
▒ ▓██░ ▒░▒▒██▒▒██░▄▄▄ ▒███  ▓██ ░▄█ ▒
░ ▓██▓ ░ ░░██░░▓█  ██ ▒▓█  ▄▒██▀▀█▄  
  ▒██▒ ░ ░░██░▒▓███▀▒▒░▒████░██▓ ▒██▒
  ▒ ░░    ░▓  ░▒   ▒ ░░░ ▒░ ░ ▒▓ ░▒▓░
    ░    ░ ▒ ░ ░   ░ ░ ░ ░    ░▒ ░ ▒ 
  ░ ░    ░ ▒ ░ ░   ░     ░    ░░   ░ 
           ░       ░ ░   ░     ░     
```
> youtube music downloader for lazy perfectionists. 

Have you ever downloaded music from youtube, but a bunch of stuff is wrong with it?
Like there's no album cover, half the tags are missing, the bitrate is questionable and the filename has the downloader's name appended at the end? Yeah, me too, that's why i've made this.

**This project is no longer maintained, as it was super seeded by [shira](https://github.com/KraXen72/shira).**
  
# features
- **fast & easy to use**. usually just hit enter a few times to confirm the tags.
- **download in the highest bitrate youtube provides** (128kbps)
- **automatically infer most of the tags** from the music video (you can enter the remaining ones) (see [smart metadata](#smart-metadata))
- **tkiner GUI** to quickly crop/pad the video thumbnail as an album cover
  - **with Drag & Drop support**: you can drop a new cover into the tkinter window to override it.
- **smart stripping/parsing of url** (youtube music, youtube, timestamp, playlist)
- **option to auto transcode** to 128kb/s (to ensure consistency) or 320kb/s (if you're a madlad, you can change it in the code lol)
  
# install & usage
```
$ pip install -r requirements.txt
```
create a `config.json` file with these options:
```json
{
    "savedir": "whatever your save dir for music is (absolute path is best)",
    "save_json_dump": false,
    "ffmpeg_location" : "not neccesary if ffmpeg is installed globally / in PATH",
    "id3v": "either '2.3' or '2.4' (not required)",
	"audio_format": "either 'opus' or 'mp3' (default)",
}
```
- **save_json_dump** is useful for debugging or if you want extra info about the song in json  
- **ffmpeg_location** is better if defined on windows unless you're sure you have `ffmpeg` in PATH.  
if you don't have `ffmpeg` in PATH, point it at a `ffmpeg` binary like so: `D:/coding/yt-dlp/ffmpeg-master-latest-win64-gpl-shared/bin/ffmpeg.exe`  
- **id3v** is the ID3 version. 2.3 has better support across music players, but dates are only kept as year, not full date. If you care about the dates, set this to 2.4, otherwise it's best to keep at 2.3
- **audio_format**: `mp3` converts the file to 128kbps `mp3`. `opus` downloads the highest quality audio (even in container) and extracts the `.opus` file out of it. Most likely will be better quality than mp3, but not all devices can play `.opus` files.
    
only thing left is to run it! `python musicdl.py` from this folder. (idk how to make it a global command *yet*)  
it is best to go directly to `music.youtube.com` (even if you don't have it paid), click on the 'song' item and paste in the `music.youtube.com/watch?v=...` link. This ensures most metadata get detected = less work for you.
  
# smart metadata
- tiger will try to get information to all of these tags for each video: `title`, `artist`, `album_artist`, `album`, `year`, and if possible, `publisher`
- it does so by first fetching as much information about the video as possible: the title, description, upload date, channel name, youtube music tags, etc.
- it extracts info from all of these sources, categorizes it and then puts each category in a "battle royale"
- this means that the item which there is the most of, wins
- for example, if we have 7 entries for Title, 5 of them are `Ergot`, 1 is `Ergot (Official Audio)` and one is `Ergot feat. Whatever`, `Ergot` wins with the most occurences
- There are also several fallbacks to solve draws between tags (sorted by importance of source)
- And also several fallbacks incase the category is empty (like filling the album to Title (Single) )
- In the end, for each category the winning tag is presented to the user, where you can either accept it or write your alternative which will be used
  
# notes
- this should be used mostly for songs that aren't on spotify, but only on youtube. If the songs is on spotify/deezer, there are tools which can download it in much higher quality. This downloads in 128kbps which is not great but not terrible. If you're okay with 128kbps, feel free to use this.
- **why python?????** cause most youtube downloading stuff is already written in python
- **why tkinter????** because i couldn't be bothered to set up flask. this works well enough.
- **why mp3????** with the medium quality youtube provides, it doesen't make sense to transcode to flac or whatever. You can pr ogg transcoding if you feel like adding it.
- **why tiger????** i had an empty bottle of tiger energy drink in front of me + it sounds cool & has a cool ascii art
- it should *in theory* be able to download full playlists but i haven't tested it.
- you can use https://greasyfork.org/en/scripts/446275-youtube-screenshoter to get any frame of an youtube video quickly (hold ctrl to download instead of clipboard)
  
# screenshots
![combinedscreenshot](screenshots/combscreen.png)

## support development
[![Recurring donation via Liberapay](https://liberapay.com/assets/widgets/donate.svg)](https://liberapay.com/KraXen72)
[![One-time donation via ko-fi.com](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/kraxen72)  
Any donations are highly appreciated! <3

## credits
- [phinger cursors](https://github.com/phisch/phinger-cursors) and [xelu's controller prompts](https://thoseawesomeguys.com/prompts/) used for instructions