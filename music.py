import youtube_dl, spotipy
import urllib.parse, urllib.request, requests, re
from discord import FFmpegPCMAudio
from discord.utils import get
from spotipy.oauth2 import SpotifyClientCredentials
servers = {}
ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials)


class Servers:
    def __init__(self, serv, vc, client):
        self.server = serv
        self.queue = []
        self.curnum = 0
        self.is_playing = False
        self.is_looping = False
        self.lq = False
        self.vc_channel = vc
        self.msgchannel = None
        self.voice_client = get(client.voice_clients)

    def play_song(self):
        self.is_playing = True
        self.voice_client.play(FFmpegPCMAudio(self.queue[self.curnum].download["url"], **FFMPEG_OPTIONS), after=lambda x: self.aftersong())

    def aftersong(self):
        if self.is_looping:
            self.play_song()
        elif self.lq and self.curnum == len(self.queue) - 1:
            self.curnum = 0
            self.play_song()
        elif self.curnum < len(self.queue) - 1:
            self.curnum += 1
            self.play_song()
        else:
            self.curnum += 1
            self.is_playing = False


class Song:
    def __init__(self, url):
        self.url = url
        self.download = self.download(self.url)
        self.durationmins = round(self.download["duration"] / 60)
        self.durationsecs = round(self.download["duration"] % 60)
        self.title = self.download["title"]

    def download(self, url):
        i = 0
        while i < 5:
            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(url, download=False)
            except youtube_dl.utils.DownloadError:
                print("403'd")
                i += 1


async def find_song_type(data, bot):
    if re.search("https://youtube.com", data) is not None:
        bot.queue.append(Song(data))
    elif re.search("https://open.spotify.com/track/", data) is not None:
        spot = requests.get(data).text
        title = re.findall("<title>.+</title>", spot)[0].replace("<title>", "").replace(" | Spotify</title>", "")
        url = await find_youtbe_song(title)
        bot.queue.append(Song(url))
    else:
        url = await find_youtbe_song(data)
        bot.queue.append(Song(url))
    if not bot.is_playing:
        bot.play_song()


async def find_youtbe_song(title):
    link = urllib.parse.urlencode({'search_query': title})
    content = urllib.request.urlopen('http://www.youtube.com/results?' + link)
    searchresult = re.findall(r'/watch\?v=(.{11})', content.read().decode())
    url = ('http://www.youtube.com/watch?v=' + searchresult[0])
    return url
