import os
import re
import textwrap

import aiofiles
import aiohttp
import numpy as np

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from youtubesearchpython.__future__ import VideosSearch

from config import YOUTUBE_IMG_URL
from Dolbymusic import app



def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


def add_corners(im):
    bigsize = (im.size[0] * 3, im.size[1] * 3)
    mask = Image.new("L", bigsize, 0)
    ImageDraw.Draw(mask).ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.LANCZOS)
    mask = ImageChops.darker(mask, im.split()[-1])
    im.putalpha(mask)


async def gen_thumb(videoid, user_id):
    # Ensure cache directory exists
    os.makedirs("cache", exist_ok=True)
    
    if os.path.isfile(f"cache/{videoid}_{user_id}.png"):
        return f"cache/{videoid}_{user_id}.png"
    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        search_results = await results.next()
        
        for result in search_results["result"]:
            try:
                title = result["title"]
                title = re.sub("\W+", " ", title)
                title = title.title()
            except Exception:
                title = "Unsupported Title"
            try:
                duration = result["duration"]
            except Exception:
                duration = "Unknown"
            try:
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            except Exception:
                thumbnail = None
            try:
                result["viewCount"]["short"]
            except:
                pass
            try:
                result["channel"]["name"]
            except:
                pass

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        try:
            wxyz = await app.get_profile_photos(user_id)
            wxy = await app.download_media(wxyz[0]['file_id'], file_name=f'{user_id}.jpg')
        except Exception:
            try:
                hehe = await app.get_profile_photos(app.id)
                wxy = await app.download_media(hehe[0]['file_id'], file_name=f'{app.id}.jpg')
            except Exception:
                # Create a default profile image
                default_img = Image.new("RGB", (640, 640), color="blue")
                wxy = f"cache/default_{user_id}.jpg"
                default_img.save(wxy)
        
        try:
            xy = Image.open(wxy)
            a = Image.new('L', [640, 640], 0)
            b = ImageDraw.Draw(a)
            b.pieslice([(0, 0), (640,640)], 0, 360, fill = 255, outline = "white")
            c = np.array(xy)
            d = np.array(a)
            e = np.dstack((c, d))
            f = Image.fromarray(e)
            x = f.resize((107, 107))
        except Exception:
            # Create a default circular profile image
            x = Image.new("RGB", (107, 107), color="blue")

        try:
            youtube = Image.open(f"cache/thumb{videoid}.png")
            bg_path = "Dolbymusic/assets/anonx.png"
            if os.path.exists(bg_path):
                bg = Image.open(bg_path)
            else:
                bg = Image.new("RGBA", (1280, 720), color=(0, 0, 0, 180))
        except Exception:
            # Create fallback images
            youtube = Image.new("RGB", (480, 360), color="gray")
            bg = Image.new("RGBA", (1280, 720), color=(0, 0, 0, 180))

        try:
            image1 = changeImageSize(1280, 720, youtube)
            image2 = image1.convert("RGBA")
            background = image2.filter(filter=ImageFilter.BoxBlur(30))
            enhancer = ImageEnhance.Brightness(background)
            background = enhancer.enhance(0.6)

            image3 = changeImageSize(1280, 720, bg)
            image5 = image3.convert("RGBA")
            composite = Image.alpha_composite(background, image5)
            composite.save(f"cache/temp{videoid}.png")
        except Exception:
            # Create a fallback composite
            fallback = Image.new("RGBA", (1280, 720), color=(50, 50, 50, 255))
            fallback.save(f"cache/temp{videoid}.png")

        try:
            Xcenter = youtube.width / 2
            Ycenter = youtube.height / 2
            x1 = Xcenter - 250
            y1 = Ycenter - 250
            x2 = Xcenter + 250
            y2 = Ycenter + 250
            logo = youtube.crop((x1, y1, x2, y2))
            logo.thumbnail((520, 520), Image.LANCZOS)
            logo.save(f"cache/chop{videoid}.png")
            
            if not os.path.isfile(f"cache/cropped{videoid}.png"):
                im = Image.open(f"cache/chop{videoid}.png").convert("RGBA")
                add_corners(im)
                im.save(f"cache/cropped{videoid}.png")
        except Exception:
            # Create a fallback cropped image
            fallback_crop = Image.new("RGBA", (365, 365), color=(100, 100, 100, 255))
            fallback_crop.save(f"cache/cropped{videoid}.png")

        try:
            crop_img = Image.open(f"cache/cropped{videoid}.png")
            logo = crop_img.convert("RGBA")
            logo.thumbnail((365, 365), Image.LANCZOS)
            width = int((1280 - 365) / 2)
            background = Image.open(f"cache/temp{videoid}.png")
            background.paste(logo, (width + 2, 138), mask=logo)
            background.paste(x, (710, 427), mask=x)
            background.paste(image3, (0, 0), mask=image3)
        except Exception:
            # Create a fallback background
            background = Image.new("RGBA", (1280, 720), color=(80, 80, 80, 255))

        try:
            draw = ImageDraw.Draw(background)
            font_path = "Dolbymusic/assets/font2.ttf"
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, 45)
                arial = ImageFont.truetype(font_path, 30)
            else:
                font = ImageFont.load_default()
                arial = ImageFont.load_default()
        except Exception:
            # Use default fonts
            font = ImageFont.load_default()
            arial = ImageFont.load_default()
        
        try:
            para = textwrap.wrap(title, width=32)
        except Exception:
            para = ["Unknown Title"]
        
        try:
            draw.text(
                (450, 25),
                f"STARTED PLAYING",
                fill="white",
                stroke_width=3,
                stroke_fill="grey",
                font=font,
            )
            
            if len(para) > 0 and para[0]:
                bbox = draw.textbbox((0, 0), f"{para[0]}", font=font)
                text_w = bbox[2] - bbox[0]
                draw.text(
                    ((1280 - text_w) / 2, 530),
                    f"{para[0]}",
                    fill="white",
                    stroke_width=1,
                    stroke_fill="white",
                    font=font,
                )
                
            if len(para) > 1 and para[1]:
                bbox = draw.textbbox((0, 0), f"{para[1]}", font=font)
                text_w = bbox[2] - bbox[0]
                draw.text(
                    ((1280 - text_w) / 2, 580),
                    f"{para[1]}",
                    fill="white",
                    stroke_width=1,
                    stroke_fill="white",
                    font=font,
                )
        except Exception:
            pass
            
        try:
            bbox = draw.textbbox((0, 0), f"Duration: {duration} Mins", font=arial)
            text_w = bbox[2] - bbox[0]
            draw.text(
                ((1280 - text_w) / 2, 660),
                f"Duration: {duration} Mins",
                fill="white",
                font=arial,
            )
        except Exception:
            pass
            
        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass
            
        try:
            background.save(f"cache/{videoid}_{user_id}.png")
            return f"cache/{videoid}_{user_id}.png"
        except Exception:
            return YOUTUBE_IMG_URL
    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL


async def gen_qthumb(videoid, user_id):
    # Ensure cache directory exists
    os.makedirs("cache", exist_ok=True)
    
    if os.path.isfile(f"cache/que{videoid}_{user_id}.png"):
        return f"cache/que{videoid}_{user_id}.png"
    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            try:
                title = result["title"]
                title = re.sub("\W+", " ", title)
                title = title.title()
            except Exception:
                title = "Unsupported Title"
            try:
                duration = result["duration"]
            except Exception:
                duration = "Unknown"
            try:
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            except Exception:
                thumbnail = None
            try:
                result["viewCount"]["short"]
            except:
                pass
            try:
                result["channel"]["name"]
            except:
                pass

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        try:
            wxyz = await app.get_profile_photos(user_id)
            wxy = await app.download_media(wxyz[0]['file_id'], file_name=f'{user_id}.jpg')
        except:
            hehe = await app.get_profile_photos(app.id)
            wxy = await app.download_media(hehe[0]['file_id'], file_name=f'{app.id}.jpg')
        xy = Image.open(wxy)
        a = Image.new('L', [640, 640], 0)
        b = ImageDraw.Draw(a)
        b.pieslice([(0, 0), (640,640)], 0, 360, fill = 255, outline = "white")
        c = np.array(xy)
        d = np.array(a)
        e = np.dstack((c, d))
        f = Image.fromarray(e)
        x = f.resize((107, 107))

        youtube = Image.open(f"cache/thumb{videoid}.png")
        bg = Image.open(f"Dolbymusic/assets/anonx.png")
        image1 = changeImageSize(1280, 720, youtube)
        image2 = image1.convert("RGBA")
        background = image2.filter(filter=ImageFilter.BoxBlur(30))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.6)

        image3 = changeImageSize(1280, 720, bg)
        image5 = image3.convert("RGBA")
        Image.alpha_composite(background, image5).save(f"cache/temp{videoid}.png")

        Xcenter = youtube.width / 2
        Ycenter = youtube.height / 2
        x1 = Xcenter - 250
        y1 = Ycenter - 250
        x2 = Xcenter + 250
        y2 = Ycenter + 250
        logo = youtube.crop((x1, y1, x2, y2))
        logo.thumbnail((520, 520), Image.LANCZOS)
        logo.save(f"cache/chop{videoid}.png")
        if not os.path.isfile(f"cache/cropped{videoid}.png"):
            im = Image.open(f"cache/chop{videoid}.png").convert("RGBA")
            add_corners(im)
            im.save(f"cache/cropped{videoid}.png")

        crop_img = Image.open(f"cache/cropped{videoid}.png")
        logo = crop_img.convert("RGBA")
        logo.thumbnail((365, 365), Image.LANCZOS)
        width = int((1280 - 365) / 2)
        background = Image.open(f"cache/temp{videoid}.png")
        background.paste(logo, (width + 2, 138), mask=logo)
        background.paste(x, (710, 427), mask=x)
        background.paste(image3, (0, 0), mask=image3)

        draw = ImageDraw.Draw(background)
        font = ImageFont.truetype("Dolbymusic/assets/font2.ttf", 45)
        ImageFont.truetype("Dolbymusic/assets/font2.ttf", 70)
        arial = ImageFont.truetype("Dolbymusic/assets/font2.ttf", 30)
        ImageFont.truetype("Dolbymusic/assets/font.ttf", 30)
        para = textwrap.wrap(title, width=32)
        try:
            draw.text(
                (455, 25),
                "ADDED TO QUEUE",
                fill="white",
                stroke_width=5,
                stroke_fill="black",
                font=font,
            )
            if len(para) > 0 and para[0]:
                bbox = draw.textbbox((0, 0), f"{para[0]}", font=font)
                text_w = bbox[2] - bbox[0]
                draw.text(
                    ((1280 - text_w) / 2, 530),
                    f"{para[0]}",
                    fill="white",
                    stroke_width=1,
                    stroke_fill="white",
                    font=font,
                )
            if len(para) > 1 and para[1]:
                bbox = draw.textbbox((0, 0), f"{para[1]}", font=font)
                text_w = bbox[2] - bbox[0]
                draw.text(
                    ((1280 - text_w) / 2, 580),
                    f"{para[1]}",
                    fill="white",
                    stroke_width=1,
                    stroke_fill="white",
                    font=font,
                )
        except:
            pass
        bbox = draw.textbbox((0, 0), f"Duration: {duration} Mins", font=arial)
        text_w = bbox[2] - bbox[0]
        draw.text(
            ((1280 - text_w) / 2, 660),
            f"Duration: {duration} Mins",
            fill="white",
            font=arial,
        )

        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass
        file = f"cache/que{videoid}_{user_id}.png"
        background.save(f"cache/que{videoid}_{user_id}.png")
        return f"cache/que{videoid}_{user_id}.png"
    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL


async def get_thumb(videoid, user_id):
    """
    Main thumbnail function that returns either cached or newly generated thumbnail
    This is the function that other modules import and use
    """
    return await gen_thumb(videoid, user_id)
