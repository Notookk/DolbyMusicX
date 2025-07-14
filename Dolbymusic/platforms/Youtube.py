# import asyncio
# import os
# import re
# import json
# from typing import Union
# from urllib.parse import urlparse, parse_qs

# import httpx
# from pyrogram.enums import MessageEntityType
# from pyrogram.types import Message
# from youtubesearchpython.__future__ import VideosSearch

# from Dolbymusic.utils.database import is_on_off
# from Dolbymusic.utils.formatters import time_to_seconds


# # ============== CONFIGURE YOUR API ==============
# YOUR_API_URL = "http://45.38.42.10:8000"
# YOUR_API_KEY = "b1569d174a144d8cb9a7df126225b181"            # <--- Change me!
# # ================================================

# async def get_file_from_api(video_id, audio=True):
#     endpoint = "/download/audio" if audio else "/download/video"
#     url = f"{YOUR_API_URL}{endpoint}"
#     params = {"video_id": video_id}
#     headers = {"x-api-key": YOUR_API_KEY}
#     async with httpx.AsyncClient(timeout=180) as client:
#         response = await client.get(url, params=params, headers=headers)
#         if response.status_code == 200:
#             ext = "mp3" if audio else "mp4"
#             os.makedirs("downloads", exist_ok=True)
#             file_path = f"downloads/{video_id}.{ext}"
#             with open(file_path, "wb") as f:
#                 f.write(response.content)
#             return file_path
#         else:
#             print("API Error:", response.status_code, response.text)
#             return None

# class YouTubeAPI:
#     def __init__(self):
#         self.base = "https://www.youtube.com/watch?v="
#         self.regex = r"(?:youtube\.com|youtu\.be)"
#         self.status = "https://www.youtube.com/oembed?url="
#         self.listbase = "https://youtube.com/playlist?list="
#         self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

#     async def exists(self, link: str, videoid: Union[bool, str] = None):
#         if videoid:
#             link = self.base + link
#         return bool(re.search(self.regex, link))

#     async def url(self, message_1: Message) -> Union[str, None]:
#         messages = [message_1]
#         if message_1.reply_to_message:
#             messages.append(message_1.reply_to_message)
#         text = ""
#         offset = None
#         length = None
#         for message in messages:
#             if offset:
#                 break
#             if message.entities:
#                 for entity in message.entities:
#                     if entity.type == MessageEntityType.URL:
#                         text = message.text or message.caption
#                         offset, length = entity.offset, entity.length
#                         break
#             elif message.caption_entities:
#                 for entity in message.caption_entities:
#                     if entity.type == MessageEntityType.TEXT_LINK:
#                         return entity.url
#         if offset is None:
#             return None
#         return text[offset : offset + length]

#     async def details(self, link: str, videoid: Union[bool, str] = None):
#         if videoid:
#             link = self.base + link
#         if "&" in link:
#             link = link.split("&")[0]
#         results = VideosSearch(link, limit=1)
#         for result in (await results.next())["result"]:
#             title = result["title"]
#             duration_min = result["duration"]
#             thumbnail = result["thumbnails"][0]["url"].split("?")[0]
#             vidid = result["id"]
#             if str(duration_min) == "None":
#                 duration_sec = 0
#             else:
#                 duration_sec = int(time_to_seconds(duration_min))
#         return title, duration_min, duration_sec, thumbnail, vidid

#     async def title(self, link: str, videoid: Union[bool, str] = None):
#         if videoid:
#             link = self.base + link
#         if "&" in link:
#             link = link.split("&")[0]
#         results = VideosSearch(link, limit=1)
#         for result in (await results.next())["result"]:
#             title = result["title"]
#         return title

#     async def duration(self, link: str, videoid: Union[bool, str] = None):
#         if videoid:
#             link = self.base + link
#         if "&" in link:
#             link = link.split("&")[0]
#         results = VideosSearch(link, limit=1)
#         for result in (await results.next())["result"]:
#             duration = result["duration"]
#         return duration

#     async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
#         if videoid:
#             link = self.base + link
#         if "&" in link:
#             link = link.split("&")[0]
#         results = VideosSearch(link, limit=1)
#         for result in (await results.next())["result"]:
#             thumbnail = result["thumbnails"][0]["url"].split("?")[0]
#         return thumbnail

#     async def video(self, link: str, videoid: Union[bool, str] = None):
#         # Extract YouTube video ID
#         if videoid:
#             link = self.base + link
#         if "&" in link:
#             link = link.split("&")[0]
#         url_data = urlparse(link)
#         if url_data.hostname and "youtube" in url_data.hostname:
#             query = parse_qs(url_data.query)
#             video_id = query.get("v", [None])[0]
#         elif url_data.hostname == "youtu.be":
#             video_id = url_data.path[1:]
#         else:
#             video_id = link  # fallback

#         file_path = await get_file_from_api(video_id, audio=False)
#         if file_path:
#             return 1, file_path
#         else:
#             return 0, "API download failed"

#     async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
#         if videoid:
#             link = self.listbase + link
#         if "&" in link:
#             link = link.split("&")[0]
#         # This still uses shell/yt-dlp for playlist ID extraction. 
#         # If your API supports playlist extraction, replace this block with an API call.
#         proc = await asyncio.create_subprocess_exec(
#             "yt-dlp",
#             "-i", "--get-id", "--flat-playlist",
#             "--playlist-end", str(limit),
#             "--skip-download", link,
#             stdout=asyncio.subprocess.PIPE,
#             stderr=asyncio.subprocess.PIPE
#         )
#         stdout, stderr = await proc.communicate()
#         if proc.returncode != 0:
#             print(f'Error:\n{stderr.decode()}')
#             return []
#         result = stdout.decode().split("\n")
#         return [r for r in result if r.strip()]

#     async def track(self, link: str, videoid: Union[bool, str] = None):
#         if videoid:
#             link = self.base + link
#         if "&" in link:
#             link = link.split("&")[0]
#         results = VideosSearch(link, limit=1)
#         for result in (await results.next())["result"]:
#             title = result["title"]
#             duration_min = result["duration"]
#             vidid = result["id"]
#             yturl = result["link"]
#             thumbnail = result["thumbnails"][0]["url"].split("?")[0]
#         track_details = {
#             "title": title,
#             "link": yturl,
#             "vidid": vidid,
#             "duration_min": duration_min,
#             "thumb": thumbnail,
#         }
#         return track_details, vidid

#     async def formats(self, link: str, videoid: Union[bool, str] = None):
#         # This is still local yt-dlp. If your API supports formats, update here.
#         import yt_dlp
#         if videoid:
#             link = self.base + link
#         if "&" in link:
#             link = link.split("&")[0]
#         ytdl_opts = {"quiet": True}
#         ydl = yt_dlp.YoutubeDL(ytdl_opts)
#         with ydl:
#             formats_available = []
#             r = ydl.extract_info(link, download=False)
#             for format in r["formats"]:
#                 try:
#                     str(format["format"])
#                 except:
#                     continue
#                 if not "dash" in str(format["format"]).lower():
#                     try:
#                         format["format"]
#                         format["filesize"]
#                         format["format_id"]
#                         format["ext"]
#                         format["format_note"]
#                     except:
#                         continue
#                     formats_available.append(
#                         {
#                             "format": format["format"],
#                             "filesize": format["filesize"],
#                             "format_id": format["format_id"],
#                             "ext": format["ext"],
#                             "format_note": format["format_note"],
#                             "yturl": link,
#                         }
#                     )
#         return formats_available, link

#     async def slider(
#         self,
#         link: str,
#         query_type: int,
#         videoid: Union[bool, str] = None,
#     ):
#         if videoid:
#             link = self.base + link
#         if "&" in link:
#             link = link.split("&")[0]
#         a = VideosSearch(link, limit=10)
#         result = (await a.next()).get("result")
#         title = result[query_type]["title"]
#         duration_min = result[query_type]["duration"]
#         vidid = result[query_type]["id"]
#         thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
#         return title, duration_min, thumbnail, vidid

#     async def download(
#         self,
#         link: str,
#         mystic,
#         video: Union[bool, str] = None,
#         videoid: Union[bool, str] = None,
#         songaudio: Union[bool, str] = None,
#         songvideo: Union[bool, str] = None,
#         format_id: Union[bool, str] = None,
#         title: Union[bool, str] = None,
#     ) -> str:
#         # Extract YouTube video ID
#         if videoid:
#             link = self.base + link
#         if "&" in link:
#             link = link.split("&")[0]
#         url_data = urlparse(link)
#         if url_data.hostname and "youtube" in url_data.hostname:
#             query = parse_qs(url_data.query)
#             video_id = query.get("v", [None])[0]
#         elif url_data.hostname == "youtu.be":
#             video_id = url_data.path[1:]
#         else:
#             video_id = link  # fallback

#         if songvideo:
#             file_path = await get_file_from_api(video_id, audio=False)
#             return file_path, True
#         elif songaudio or not video:  # Default to audio if not video
#             file_path = await get_file_from_api(video_id, audio=True)
#             return file_path, True
#         elif video:
#             file_path = await get_file_from_api(video_id, audio=False)
#             return file_path, True
#         else:
#             file_path = await get_file_from_api(video_id, audio=True)
#             return file_path, True



import re
from typing import Union
from pytubefix import YouTube, Playlist
import asyncio
import functools
import os

YOUTUBE_URL_RE = re.compile(
    r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$'
)
def is_youtube_url(text: str) -> bool:
    if not isinstance(text, str):
        return False
    return bool(YOUTUBE_URL_RE.match(text.strip()))

async def get_file_with_pytubefix(video_id, audio=True):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, functools.partial(sync_download, video_id, audio))

def sync_download(video_id, audio=True):
    url = f"https://www.youtube.com/watch?v={video_id}"
    yt = YouTube(url)
    os.makedirs("downloads", exist_ok=True)
    if audio:
        stream = yt.streams.filter(only_audio=True).first()
        ext = "mp3"
    else:
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        ext = "mp4"
    if stream is None:
        raise Exception("No suitable stream found for download")
    file_path = f"downloads/{video_id}.{ext}"
    stream.download(output_path="downloads", filename=f"{video_id}.{ext}")
    return file_path

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + str(link)
        return is_youtube_url(link)

    async def url(self, message_1) -> Union[str, None]:
        messages = [message_1]
        if hasattr(message_1, "reply_to_message") and getattr(message_1, "reply_to_message", None):
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            entities = getattr(message, "entities", None) or []
            caption_entities = getattr(message, "caption_entities", None) or []
            if offset:
                break
            if entities:
                for entity in entities:
                    etype = getattr(entity, "type", None)
                    if hasattr(etype, "name"):
                        etype = etype.name
                    if etype == "URL":
                        text = getattr(message, "text", None) or getattr(message, "caption", None) or ""
                        offset, length = entity.offset, entity.length
                        break
            if caption_entities:
                for entity in caption_entities:
                    etype = getattr(entity, "type", None)
                    if hasattr(etype, "name"):
                        etype = etype.name
                    if etype == "TEXT_LINK":
                        return getattr(entity, "url", None)
        if offset is None or not text:
            return None
        return text[offset : offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + str(link)
        if not link or not isinstance(link, str):
            return {
                "title": None,
                "duration_min": None,
                "duration_sec": None,
                "thumbnail": None,
                "vidid": None
            }
        if "&" in link:
            link = link.split("&")[0]
        loop = asyncio.get_event_loop()
        try:
            yt = await loop.run_in_executor(None, lambda: YouTube(link))
            title = yt.title
            duration_sec = getattr(yt, "length", None)
            if duration_sec is not None:
                duration_min = f"{duration_sec // 60}:{duration_sec % 60:02d}"
            else:
                duration_min = None
            thumbnail = yt.thumbnail_url
            vidid = yt.video_id
            return {
                "title": title,
                "duration_min": duration_min,
                "duration_sec": duration_sec,
                "thumbnail": thumbnail,
                "vidid": vidid
            }
        except Exception as e:
            print(f"Failed to fetch details: {e}")
            return {
                "title": None,
                "duration_min": None,
                "duration_sec": None,
                "thumbnail": None,
                "vidid": None
            }

    async def track(self, query: str, videoid: Union[bool, str] = None):
        link = None
        if videoid:
            link = self.base + str(query)
        elif is_youtube_url(query):
            link = query
        else:
            try:
                from youtubesearchpython.__future__ import VideosSearch
                search = VideosSearch(query, limit=1)
                results = await search.next()
                if not results or "result" not in results or not results["result"]:
                    raise Exception("No YouTube results found")
                first = results["result"][0]
                link = first.get("link")
            except Exception as e:
                print(f"Failed to search YouTube: {e}")
                return {
                    "title": None,
                    "link": None,
                    "vidid": None,
                    "duration_min": None,
                    "thumb": None
                }, None
        details = await self.details(link)
        if not details or not details.get("vidid"):
            return {
                "title": None,
                "link": None,
                "vidid": None,
                "duration_min": None,
                "thumb": None
            }, None
        details["thumb"] = details.get("thumbnail")
        details["link"] = link
        return details, details["vidid"]

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + str(link)
        if "&" in link:
            link = link.split("&")[0]
        loop = asyncio.get_event_loop()
        try:
            pl = await loop.run_in_executor(None, lambda: Playlist(link))
            ids = [video.video_id for video in getattr(pl, "videos", [])[:limit] if hasattr(video, "video_id")]
            return ids
        except Exception as e:
            print(f"Failed to fetch playlist: {e}")
            return []

    async def slider(self, query: str, query_type: int, videoid: Union[bool, str] = None):
        try:
            from youtubesearchpython.__future__ import VideosSearch
            search = VideosSearch(query, limit=10)
            results = await search.next()
            if not results or "result" not in results or not results["result"]:
                raise Exception("No YouTube results found")
            result = results["result"]
            if query_type >= len(result):
                raise Exception("Requested index out of search result range")
            first = result[query_type]
            title = first.get("title")
            duration_min = first.get("duration")
            vidid = first.get("id")
            thumbnail = first.get("thumbnails", [{}])[0].get("url", "").split("?")[0]
            return title, duration_min, thumbnail, vidid
        except Exception as e:
            print(f"Failed to slider-search YouTube: {e}")
            return None, None, None, None

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + str(link)
        if "&" in link:
            link = link.split("&")[0]
        loop = asyncio.get_event_loop()
        try:
            yt = await loop.run_in_executor(None, lambda: YouTube(link))
            return yt.title
        except Exception as e:
            print(f"Failed to fetch title: {e}")
            return None

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + str(link)
        if "&" in link:
            link = link.split("&")[0]
        loop = asyncio.get_event_loop()
        try:
            yt = await loop.run_in_executor(None, lambda: YouTube(link))
            duration_sec = getattr(yt, "length", None)
            if duration_sec is not None:
                return f"{duration_sec // 60}:{duration_sec % 60:02d}"
            return None
        except Exception as e:
            print(f"Failed to fetch duration: {e}")
            return None

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + str(link)
        if "&" in link:
            link = link.split("&")[0]
        loop = asyncio.get_event_loop()
        try:
            yt = await loop.run_in_executor(None, lambda: YouTube(link))
            return yt.thumbnail_url
        except Exception as e:
            print(f"Failed to fetch thumbnail: {e}")
            return None

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + str(link)
        if "&" in link:
            link = link.split("&")[0]
        video_id = None
        try:
            from urllib.parse import urlparse, parse_qs
            url_data = urlparse(link)
            if url_data.hostname and "youtube" in url_data.hostname:
                query = parse_qs(url_data.query)
                video_id = query.get("v", [None])[0]
            elif url_data.hostname == "youtu.be":
                video_id = url_data.path[1:]
            else:
                video_id = link
            file_path = await get_file_with_pytubefix(video_id, audio=False)
            return 1, file_path
        except Exception as e:
            print(f"Failed to download video: {e}")
            return 0, "Download failed"

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + str(link)
        if "&" in link:
            link = link.split("&")[0]
        video_id = None
        try:
            from urllib.parse import urlparse, parse_qs
            url_data = urlparse(link)
            if url_data.hostname and "youtube" in url_data.hostname:
                query = parse_qs(url_data.query)
                video_id = query.get("v", [None])[0]
            elif url_data.hostname == "youtu.be":
                video_id = url_data.path[1:]
            else:
                video_id = link
            loop = asyncio.get_event_loop()
            yt = await loop.run_in_executor(None, lambda: YouTube(f"https://www.youtube.com/watch?v={video_id}"))
            formats_available = []
            for stream in yt.streams:
                formats_available.append({
                    "itag": getattr(stream, "itag", None),
                    "mime_type": getattr(stream, "mime_type", None),
                    "abr": getattr(stream, "abr", None),
                    "resolution": getattr(stream, "resolution", None),
                    "type": "audio" if getattr(stream, "only_audio", False) else "video",
                    "ext": getattr(stream, "subtype", None),
                    "filesize": getattr(stream, "filesize", None),
                    "yturl": yt.watch_url,
                })
            return formats_available, yt.watch_url
        except Exception as e:
            print(f"Failed to fetch formats: {e}")
            return [], None

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
            link = self.base + str(link)
        if "&" in link:
            link = link.split("&")[0]
        video_id = None
        try:
            from urllib.parse import urlparse, parse_qs
            url_data = urlparse(link)
            if url_data.hostname and "youtube" in url_data.hostname:
                query = parse_qs(url_data.query)
                video_id = query.get("v", [None])[0]
            elif url_data.hostname == "youtu.be":
                video_id = url_data.path[1:]
            else:
                video_id = link
            if songvideo:
                file_path = await get_file_with_pytubefix(video_id, audio=False)
                return file_path, True
            elif songaudio or not video:
                file_path = await get_file_with_pytubefix(video_id, audio=True)
                return file_path, True
            elif video:
                file_path = await get_file_with_pytubefix(video_id, audio=False)
                return file_path, True
            else:
                file_path = await get_file_with_pytubefix(video_id, audio=True)
                return file_path, True
        except Exception as e:
            print(f"Failed to download: {e}")
            return None, False
