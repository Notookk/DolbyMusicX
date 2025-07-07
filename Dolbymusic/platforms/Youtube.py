import asyncio
import os
import re
import json
from typing import Union
from pytubefix import YouTube, Playlist
from pytubefix.exceptions import VideoUnavailable, PytubeFixError
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch

from Dolbymusic.utils.database import is_on_off
from Dolbymusic.utils.formatters import time_to_seconds


class YouTubeAPI:
    def __init__(self):
        # ✅ Write the OAuth token file on initialization
        TOKEN_DATA = {
            "access_token": "ya29.a0AS3H6NzLXdSTjpBVusjfcw5WZZiMh2ZIjZT_lUZ4jTnOa9fVD3G1zWuZQI35GUaB0kd69KyD0hWo4SGE6hYlOFsInVPkV4DVdVr66UcXoXrWYspwxkxSUQnZ6pKZKO7jB1HImZSxi_tQ21C8dVbeYvtwX1lVkXgdKZ_qwOA7gOI0Hm-vNtR_aCgYKAbASARESFQHGX2MibBmOfIa46ysoUL5Mho3g4A0187",
            "refresh_token": "1//0gQuq_8NitjNtCgYIARAAGBASNwF-L9IrjHz83LLWl5lJg8A3A_27fO4FqpgSF2EVbcc4UXz4cglyEiFPvTDicWu1vb2Ke79yPv4",
            "expires": 1751988208,
            "visitorData": None,
            "po_token": None
        }
        with open(".pytube-oauth.json", "w") as f:
            json.dump(TOKEN_DATA, f)

        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    def _create_youtube_object(self, url: str):
        """Create YouTube object with OAuth authentication to avoid bot detection"""
        try:
            return YouTube(url, use_oauth=True, allow_oauth_cache=True)
        except Exception:
            # Fallback without OAuth if it fails
            return YouTube(url)

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if re.search(self.regex, link):
            return True
        else:
            return False

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset in (None,):
            return None
        return text[offset : offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        # Try pytubefix first, fallback to VideosSearch
        try:
            loop = asyncio.get_running_loop()
            yt = await loop.run_in_executor(None, self._create_youtube_object, link)
            title = yt.title
            duration_sec = yt.length
            duration_min = f"{duration_sec // 60}:{duration_sec % 60:02d}"
            thumbnail = yt.thumbnail_url
            vidid = yt.video_id
            return title, duration_min, duration_sec, thumbnail, vidid
        except Exception:
            # Fallback to VideosSearch
            results = VideosSearch(link, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration_min = result["duration"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                vidid = result["id"]
                if str(duration_min) == "None":
                    duration_sec = 0
                else:
                    duration_sec = int(time_to_seconds(duration_min))
            return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        try:
            loop = asyncio.get_running_loop()
            yt = await loop.run_in_executor(None, self._create_youtube_object, link)
            return yt.title
        except Exception:
            results = VideosSearch(link, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
            return title

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        try:
            loop = asyncio.get_running_loop()
            yt = await loop.run_in_executor(None, self._create_youtube_object, link)
            duration_sec = yt.length
            return f"{duration_sec // 60}:{duration_sec % 60:02d}"
        except Exception:
            results = VideosSearch(link, limit=1)
            for result in (await results.next())["result"]:
                duration = result["duration"]
            return duration

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        try:
            loop = asyncio.get_running_loop()
            yt = await loop.run_in_executor(None, self._create_youtube_object, link)
            return yt.thumbnail_url
        except Exception:
            results = VideosSearch(link, limit=1)
            for result in (await results.next())["result"]:
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            return thumbnail

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        try:
            loop = asyncio.get_running_loop()
            yt = await loop.run_in_executor(None, self._create_youtube_object, link)
            
            # Get progressive stream first (video+audio in one file)
            stream = yt.streams.filter(progressive=True, res="720p").first()
            if not stream:
                stream = yt.streams.filter(progressive=True).get_highest_resolution()
            
            if stream:
                return 1, stream.url
            else:
                # Try adaptive video stream
                stream = yt.streams.filter(only_video=True, res="720p").first()
                if not stream:
                    stream = yt.streams.filter(only_video=True).get_highest_resolution()
                return 1, stream.url if stream else None
        except Exception as e:
            return 0, str(e)

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        
        try:
            loop = asyncio.get_running_loop()
            
            def get_playlist_videos():
                playlist = Playlist(link)
                videos = []
                count = 0
                for video in playlist.videos:
                    if count >= limit:
                        break
                    videos.append(video.video_id)
                    count += 1
                return videos
            
            result = await loop.run_in_executor(None, get_playlist_videos)
            return result
        except Exception:
            return []

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        try:
            loop = asyncio.get_running_loop()
            yt = await loop.run_in_executor(None, self._create_youtube_object, link)
            title = yt.title
            duration_sec = yt.length
            duration_min = f"{duration_sec // 60}:{duration_sec % 60:02d}"
            vidid = yt.video_id
            yturl = link
            thumbnail = yt.thumbnail_url
            track_details = {
                "title": title,
                "link": yturl,
                "vidid": vidid,
                "duration_min": duration_min,
                "thumb": thumbnail,
            }
            return track_details, vidid
        except Exception:
            # Fallback to VideosSearch
            results = VideosSearch(link, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration_min = result["duration"]
                vidid = result["id"]
                yturl = result["link"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            track_details = {
                "title": title,
                "link": yturl,
                "vidid": vidid,
                "duration_min": duration_min,
                "thumb": thumbnail,
            }
            return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        try:
            loop = asyncio.get_running_loop()
            yt = await loop.run_in_executor(None, self._create_youtube_object, link)
            
            formats_available = []
            
            # Get all available streams
            for stream in yt.streams.filter(progressive=False):
                if stream.filesize is None:
                    continue
                
                # Create format info compatible with existing code
                format_info = {
                    "format": f"{stream.itag} - {stream.mime_type}",
                    "filesize": stream.filesize,
                    "format_id": str(stream.itag),
                    "ext": stream.subtype,
                    "format_note": f"{stream.resolution or stream.abr} {stream.type}",
                    "yturl": link,
                }
                formats_available.append(format_info)
            
            return formats_available, link
        except Exception:
            return [], link

    async def slider(
        self,
        link: str,
        query_type: int,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid:
            link = self.base + link
        loop = asyncio.get_running_loop()

        def audio_dl():
            yt = self._create_youtube_object(link)
            
            # Get audio stream
            stream = yt.streams.get_audio_only()
            if not stream:
                stream = yt.streams.filter(only_audio=True).first()
            
            if stream:
                filename = f"downloads/{yt.video_id}.{stream.subtype}"
                if os.path.exists(filename):
                    return filename
                stream.download(output_path="downloads", filename=f"{yt.video_id}.{stream.subtype}")
                return filename
            return None

        def video_dl():
            yt = self._create_youtube_object(link)
            
            # Get progressive video stream (video+audio)
            stream = yt.streams.filter(progressive=True, res="720p").first()
            if not stream:
                stream = yt.streams.filter(progressive=True).get_highest_resolution()
            
            if stream:
                filename = f"downloads/{yt.video_id}.{stream.subtype}"
                if os.path.exists(filename):
                    return filename
                stream.download(output_path="downloads", filename=f"{yt.video_id}.{stream.subtype}")
                return filename
            return None

        def song_video_dl():
            yt = self._create_youtube_object(link)
            
            # Get specific format by itag
            stream = yt.streams.get_by_itag(int(format_id)) if format_id else None
            if not stream:
                stream = yt.streams.filter(progressive=True).get_highest_resolution()
            
            if stream:
                filename = f"downloads/{title}.{stream.subtype}"
                stream.download(output_path="downloads", filename=f"{title}.{stream.subtype}")
                return filename
            return None

        def song_audio_dl():
            yt = self._create_youtube_object(link)
            
            # Get specific audio format by itag
            stream = yt.streams.get_by_itag(int(format_id)) if format_id else None
            if not stream:
                stream = yt.streams.get_audio_only()
            
            if stream:
                filename = f"downloads/{title}.{stream.subtype}"
                stream.download(output_path="downloads", filename=f"{title}.{stream.subtype}")
                # Convert to mp3 if needed (pytubefix downloads as original format)
                if stream.subtype != "mp3":
                    # For now, return the original file - you can add conversion logic here
                    pass
                return filename
            return None

        try:
            if songvideo:
                downloaded_file = await loop.run_in_executor(None, song_video_dl)
                return downloaded_file or f"downloads/{title}.mp4"
            elif songaudio:
                downloaded_file = await loop.run_in_executor(None, song_audio_dl)
                return downloaded_file or f"downloads/{title}.mp3"
            elif video:
                if await is_on_off(1):
                    direct = True
                    downloaded_file = await loop.run_in_executor(None, video_dl)
                else:
                    # Get direct stream URL instead of downloading
                    yt = await loop.run_in_executor(None, self._create_youtube_object, link)
                    stream = yt.streams.filter(progressive=True, res="720p").first()
                    if not stream:
                        stream = yt.streams.filter(progressive=True).get_highest_resolution()
                    
                    if stream:
                        downloaded_file = stream.url
                        direct = None
                    else:
                        return None
            else:
                direct = True
                downloaded_file = await loop.run_in_executor(None, audio_dl)
            
            return downloaded_file, direct
        except Exception as e:
            print(f"Download error: {e}")
            return None
