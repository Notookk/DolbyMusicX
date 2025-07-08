# import os
# import re
# import textwrap

# import aiofiles
# import aiohttp
# import numpy as np

# from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont
# from youtubesearchpython.__future__ import VideosSearch

# from config import YOUTUBE_IMG_URL
# from Dolbymusic import app



# def changeImageSize(maxWidth, maxHeight, image):
#     widthRatio = maxWidth / image.size[0]
#     heightRatio = maxHeight / image.size[1]
#     newWidth = int(widthRatio * image.size[0])
#     newHeight = int(heightRatio * image.size[1])
#     newImage = image.resize((newWidth, newHeight))
#     return newImage


# def add_corners(im):
#     bigsize = (im.size[0] * 3, im.size[1] * 3)
#     mask = Image.new("L", bigsize, 0)
#     ImageDraw.Draw(mask).ellipse((0, 0) + bigsize, fill=255)
#     mask = mask.resize(im.size, Image.LANCZOS)
#     mask = ImageChops.darker(mask, im.split()[-1])
#     im.putalpha(mask)


# async def gen_thumb(videoid, user_id):
#     # Ensure cache directory exists
#     os.makedirs("cache", exist_ok=True)
    
#     if os.path.isfile(f"cache/{videoid}_{user_id}.png"):
#         return f"cache/{videoid}_{user_id}.png"
#     url = f"https://www.youtube.com/watch?v={videoid}"
#     try:
#         results = VideosSearch(url, limit=1)
#         search_results = await results.next()
        
#         for result in search_results["result"]:
#             try:
#                 title = result["title"]
#                 title = re.sub("\W+", " ", title)
#                 title = title.title()
#             except Exception:
#                 title = "Unsupported Title"
#             try:
#                 duration = result["duration"]
#             except Exception:
#                 duration = "Unknown"
#             try:
#                 thumbnail = result["thumbnails"][0]["url"].split("?")[0]
#             except Exception:
#                 thumbnail = None
#             try:
#                 result["viewCount"]["short"]
#             except:
#                 pass
#             try:
#                 result["channel"]["name"]
#             except:
#                 pass

#         async with aiohttp.ClientSession() as session:
#             async with session.get(thumbnail) as resp:
#                 if resp.status == 200:
#                     f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
#                     await f.write(await resp.read())
#                     await f.close()

#         # Try to get user profile photo - simplified approach
#         wxy = None
#         try:
#             # First try to get user's profile photos
#             user_photos = await app.get_chat_photos(user_id)
#             if user_photos.total_count > 0:
#                 # Try different ways to access the photo
#                 try:
#                     # Method 1: Direct access to first photo
#                     photo_file = await app.download_media(
#                         user_photos.photos[0], 
#                         file_name=f"cache/user_{user_id}.jpg"
#                     )
#                     wxy = photo_file
#                     print(f"Method 1: Successfully downloaded user {user_id} profile photo")
#                 except:
#                     try:
#                         # Method 2: Access largest size
#                         photo_file = await app.download_media(
#                             user_photos.photos[0][-1], 
#                             file_name=f"cache/user_{user_id}.jpg"
#                         )
#                         wxy = photo_file
#                         print(f"Method 2: Successfully downloaded user {user_id} profile photo")
#                     except:
#                         # Method 3: Try smallest size
#                         photo_file = await app.download_media(
#                             user_photos.photos[0][0], 
#                             file_name=f"cache/user_{user_id}.jpg"
#                         )
#                         wxy = photo_file
#                         print(f"Method 3: Successfully downloaded user {user_id} profile photo")
#             else:
#                 print(f"User {user_id} has no profile photos")
#                 raise Exception("User has no profile photos")
#         except Exception as e:
#             print(f"Failed to get user profile photo: {e}")
#             try:
#                 # Fallback to bot's profile photo
#                 bot_photos = await app.get_chat_photos(app.id)
#                 if bot_photos.total_count > 0:
#                     try:
#                         # Method 1: Direct access
#                         photo_file = await app.download_media(
#                             bot_photos.photos[0], 
#                             file_name=f"cache/bot_{app.id}.jpg"
#                         )
#                         wxy = photo_file
#                         print(f"Using bot profile photo as fallback")
#                     except:
#                         try:
#                             # Method 2: Largest size
#                             photo_file = await app.download_media(
#                                 bot_photos.photos[0][-1], 
#                                 file_name=f"cache/bot_{app.id}.jpg"
#                             )
#                             wxy = photo_file
#                             print(f"Using bot profile photo as fallback (method 2)")
#                         except:
#                             # Method 3: Smallest size
#                             photo_file = await app.download_media(
#                                 bot_photos.photos[0][0], 
#                                 file_name=f"cache/bot_{app.id}.jpg"
#                             )
#                             wxy = photo_file
#                             print(f"Using bot profile photo as fallback (method 3)")
#                 else:
#                     raise Exception("Bot also has no profile photos")
#             except Exception as e2:
#                 print(f"Failed to get bot profile photo: {e2}")
#                 # Create a default profile image - improved design
#                 default_img = Image.new("RGB", (640, 640), color="#2C3E50")
#                 draw = ImageDraw.Draw(default_img)
                
#                 # Create a nice user avatar with initials background
#                 draw.ellipse([(50, 50), (590, 590)], fill="#3498DB", outline="#2980B9", width=10)
                
#                 # Add a simple "user" icon effect
#                 # Head circle
#                 draw.ellipse([(220, 180), (420, 380)], fill="#ECF0F1")
#                 # Body arc
#                 draw.ellipse([(120, 350), (520, 750)], fill="#ECF0F1")
                
#                 wxy = f"cache/default_{user_id}.jpg"
#                 default_img.save(wxy)
#                 print(f"Created enhanced default profile image at {wxy}")
        
#         # Process the profile image to make it circular - simplified
#         try:
#             # Open and process the profile image
#             xy = Image.open(wxy)
#             # Convert to RGB if needed
#             if xy.mode not in ("RGB", "RGBA"):
#                 xy = xy.convert("RGB")
#             # Resize to 640x640 first
#             xy = xy.resize((640, 640), Image.LANCZOS)
            
#             # Create circular mask - simplified approach
#             mask = Image.new('L', (640, 640), 0)
#             draw_mask = ImageDraw.Draw(mask)
#             draw_mask.ellipse([(0, 0), (640, 640)], fill=255)
            
#             # Create the final circular image
#             circular_img = Image.new("RGBA", (640, 640), (0, 0, 0, 0))
#             circular_img.paste(xy, (0, 0))
#             circular_img.putalpha(mask)
            
#             # Resize to final size for thumbnail
#             x = circular_img.resize((107, 107), Image.LANCZOS)
#             print(f"Successfully processed profile image to circular format")
#         except Exception as e:
#             print(f"Failed to process profile image: {e}")
#             # Create a simple fallback circular profile image
#             x = Image.new("RGBA", (107, 107), (0, 0, 0, 0))
#             draw = ImageDraw.Draw(x)
#             # Nice blue circle with user icon
#             draw.ellipse([(2, 2), (105, 105)], fill="#3498DB", outline="#2980B9", width=2)
#             # Simple user icon
#             draw.ellipse([(35, 25), (72, 62)], fill="white")  # Head
#             draw.ellipse([(20, 65), (87, 132)], fill="white")  # Body
#             print("Created enhanced fallback circular profile image")

#         try:
#             youtube = Image.open(f"cache/thumb{videoid}.png")
#             bg_path = "Dolbymusic/assets/anonx.png"
#             if os.path.exists(bg_path):
#                 bg = Image.open(bg_path)
#             else:
#                 bg = Image.new("RGBA", (1280, 720), color=(0, 0, 0, 180))
#         except Exception:
#             # Create fallback images
#             youtube = Image.new("RGB", (480, 360), color="gray")
#             bg = Image.new("RGBA", (1280, 720), color=(0, 0, 0, 180))

#         try:
#             image1 = changeImageSize(1280, 720, youtube)
#             image2 = image1.convert("RGBA")
#             background = image2.filter(filter=ImageFilter.BoxBlur(30))
#             enhancer = ImageEnhance.Brightness(background)
#             background = enhancer.enhance(0.6)

#             image3 = changeImageSize(1280, 720, bg)
#             image5 = image3.convert("RGBA")
#             composite = Image.alpha_composite(background, image5)
#             composite.save(f"cache/temp{videoid}.png")
#         except Exception:
#             # Create a fallback composite
#             fallback = Image.new("RGBA", (1280, 720), color=(50, 50, 50, 255))
#             fallback.save(f"cache/temp{videoid}.png")

#         try:
#             Xcenter = youtube.width / 2
#             Ycenter = youtube.height / 2
#             x1 = Xcenter - 250
#             y1 = Ycenter - 250
#             x2 = Xcenter + 250
#             y2 = Ycenter + 250
#             logo = youtube.crop((x1, y1, x2, y2))
#             logo.thumbnail((520, 520), Image.LANCZOS)
#             logo.save(f"cache/chop{videoid}.png")
            
#             if not os.path.isfile(f"cache/cropped{videoid}.png"):
#                 im = Image.open(f"cache/chop{videoid}.png").convert("RGBA")
#                 add_corners(im)
#                 im.save(f"cache/cropped{videoid}.png")
#         except Exception:
#             # Create a fallback cropped image
#             fallback_crop = Image.new("RGBA", (365, 365), color=(100, 100, 100, 255))
#             fallback_crop.save(f"cache/cropped{videoid}.png")

#         try:
#             crop_img = Image.open(f"cache/cropped{videoid}.png")
#             logo = crop_img.convert("RGBA")
#             logo.thumbnail((365, 365), Image.LANCZOS)
#             width = int((1280 - 365) / 2)
#             background = Image.open(f"cache/temp{videoid}.png")
#             background.paste(logo, (width + 2, 138), mask=logo)
            
#             # Paste the profile image with proper handling
#             if x.mode != "RGBA":
#                 x = x.convert("RGBA")
#             background.paste(x, (710, 427), mask=x)
#             background.paste(image3, (0, 0), mask=image3)
#             print(f"Successfully composed final thumbnail with profile image")
#         except Exception as e:
#             print(f"Failed to compose final thumbnail: {e}")
#             # Create a fallback background
#             background = Image.new("RGBA", (1280, 720), color=(80, 80, 80, 255))

#         try:
#             draw = ImageDraw.Draw(background)
#             font_path = "Dolbymusic/assets/font2.ttf"
#             if os.path.exists(font_path):
#                 font = ImageFont.truetype(font_path, 45)
#                 arial = ImageFont.truetype(font_path, 30)
#             else:
#                 font = ImageFont.load_default()
#                 arial = ImageFont.load_default()
#         except Exception:
#             # Use default fonts
#             font = ImageFont.load_default()
#             arial = ImageFont.load_default()
        
#         try:
#             para = textwrap.wrap(title, width=32)
#         except Exception:
#             para = ["Unknown Title"]
        
#         try:
#             draw.text(
#                 (450, 25),
#                 f"STARTED PLAYING",
#                 fill="white",
#                 stroke_width=3,
#                 stroke_fill="grey",
#                 font=font,
#             )
            
#             if len(para) > 0 and para[0]:
#                 bbox = draw.textbbox((0, 0), f"{para[0]}", font=font)
#                 text_w = bbox[2] - bbox[0]
#                 draw.text(
#                     ((1280 - text_w) / 2, 530),
#                     f"{para[0]}",
#                     fill="white",
#                     stroke_width=1,
#                     stroke_fill="white",
#                     font=font,
#                 )
                
#             if len(para) > 1 and para[1]:
#                 bbox = draw.textbbox((0, 0), f"{para[1]}", font=font)
#                 text_w = bbox[2] - bbox[0]
#                 draw.text(
#                     ((1280 - text_w) / 2, 580),
#                     f"{para[1]}",
#                     fill="white",
#                     stroke_width=1,
#                     stroke_fill="white",
#                     font=font,
#                 )
#         except Exception:
#             pass
            
#         try:
#             bbox = draw.textbbox((0, 0), f"Duration: {duration} Mins", font=arial)
#             text_w = bbox[2] - bbox[0]
#             draw.text(
#                 ((1280 - text_w) / 2, 660),
#                 f"Duration: {duration} Mins",
#                 fill="white",
#                 font=arial,
#             )
#         except Exception:
#             pass
            
#         try:
#             os.remove(f"cache/thumb{videoid}.png")
#         except:
#             pass
            
#         try:
#             background.save(f"cache/{videoid}_{user_id}.png")
#             return f"cache/{videoid}_{user_id}.png"
#         except Exception:
#             return YOUTUBE_IMG_URL
#     except Exception as e:
#         print(e)
#         return YOUTUBE_IMG_URL


# async def gen_qthumb(videoid, user_id):
#     # Ensure cache directory exists
#     os.makedirs("cache", exist_ok=True)
    
#     if os.path.isfile(f"cache/que{videoid}_{user_id}.png"):
#         return f"cache/que{videoid}_{user_id}.png"
#     url = f"https://www.youtube.com/watch?v={videoid}"
#     try:
#         results = VideosSearch(url, limit=1)
#         for result in (await results.next())["result"]:
#             try:
#                 title = result["title"]
#                 title = re.sub("\W+", " ", title)
#                 title = title.title()
#             except Exception:
#                 title = "Unsupported Title"
#             try:
#                 duration = result["duration"]
#             except Exception:
#                 duration = "Unknown"
#             try:
#                 thumbnail = result["thumbnails"][0]["url"].split("?")[0]
#             except Exception:
#                 thumbnail = None
#             try:
#                 result["viewCount"]["short"]
#             except:
#                 pass
#             try:
#                 result["channel"]["name"]
#             except:
#                 pass

#         async with aiohttp.ClientSession() as session:
#             async with session.get(thumbnail) as resp:
#                 if resp.status == 200:
#                     f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
#                     await f.write(await resp.read())
#                     await f.close()

#         # Try to get user profile photo - simplified approach (same as gen_thumb)
#         wxy = None
#         try:
#             # First try to get user's profile photos
#             user_photos = await app.get_chat_photos(user_id)
#             if user_photos.total_count > 0:
#                 # Try different ways to access the photo
#                 try:
#                     # Method 1: Direct access to first photo
#                     photo_file = await app.download_media(
#                         user_photos.photos[0], 
#                         file_name=f"cache/user_{user_id}.jpg"
#                     )
#                     wxy = photo_file
#                     print(f"Method 1: Successfully downloaded user {user_id} profile photo for queue")
#                 except:
#                     try:
#                         # Method 2: Access largest size
#                         photo_file = await app.download_media(
#                             user_photos.photos[0][-1], 
#                             file_name=f"cache/user_{user_id}.jpg"
#                         )
#                         wxy = photo_file
#                         print(f"Method 2: Successfully downloaded user {user_id} profile photo for queue")
#                     except:
#                         # Method 3: Try smallest size
#                         photo_file = await app.download_media(
#                             user_photos.photos[0][0], 
#                             file_name=f"cache/user_{user_id}.jpg"
#                         )
#                         wxy = photo_file
#                         print(f"Method 3: Successfully downloaded user {user_id} profile photo for queue")
#             else:
#                 print(f"User {user_id} has no profile photos")
#                 raise Exception("User has no profile photos")
#         except Exception as e:
#             print(f"Failed to get user profile photo for queue: {e}")
#             try:
#                 # Fallback to bot's profile photo
#                 bot_photos = await app.get_chat_photos(app.id)
#                 if bot_photos.total_count > 0:
#                     try:
#                         # Method 1: Direct access
#                         photo_file = await app.download_media(
#                             bot_photos.photos[0], 
#                             file_name=f"cache/bot_{app.id}.jpg"
#                         )
#                         wxy = photo_file
#                         print(f"Using bot profile photo as fallback for queue")
#                     except:
#                         try:
#                             # Method 2: Largest size
#                             photo_file = await app.download_media(
#                                 bot_photos.photos[0][-1], 
#                                 file_name=f"cache/bot_{app.id}.jpg"
#                             )
#                             wxy = photo_file
#                             print(f"Using bot profile photo as fallback for queue (method 2)")
#                         except:
#                             # Method 3: Smallest size
#                             photo_file = await app.download_media(
#                                 bot_photos.photos[0][0], 
#                                 file_name=f"cache/bot_{app.id}.jpg"
#                             )
#                             wxy = photo_file
#                             print(f"Using bot profile photo as fallback for queue (method 3)")
#                 else:
#                     raise Exception("Bot also has no profile photos")
#             except Exception as e2:
#                 print(f"Failed to get bot profile photo for queue: {e2}")
#                 # Create a default profile image - improved design
#                 default_img = Image.new("RGB", (640, 640), color="#2C3E50")
#                 draw = ImageDraw.Draw(default_img)
                
#                 # Create a nice user avatar with initials background
#                 draw.ellipse([(50, 50), (590, 590)], fill="#3498DB", outline="#2980B9", width=10)
                
#                 # Add a simple "user" icon effect
#                 # Head circle
#                 draw.ellipse([(220, 180), (420, 380)], fill="#ECF0F1")
#                 # Body arc
#                 draw.ellipse([(120, 350), (520, 750)], fill="#ECF0F1")
                
#                 wxy = f"cache/default_{user_id}.jpg"
#                 default_img.save(wxy)
#                 print(f"Created enhanced default profile image for queue at {wxy}")
        
#         # Process the profile image to make it circular - simplified
#         try:
#             # Open and process the profile image
#             xy = Image.open(wxy)
#             # Convert to RGB if needed
#             if xy.mode not in ("RGB", "RGBA"):
#                 xy = xy.convert("RGB")
#             # Resize to 640x640 first
#             xy = xy.resize((640, 640), Image.LANCZOS)
            
#             # Create circular mask - simplified approach
#             mask = Image.new('L', (640, 640), 0)
#             draw_mask = ImageDraw.Draw(mask)
#             draw_mask.ellipse([(0, 0), (640, 640)], fill=255)
            
#             # Create the final circular image
#             circular_img = Image.new("RGBA", (640, 640), (0, 0, 0, 0))
#             circular_img.paste(xy, (0, 0))
#             circular_img.putalpha(mask)
            
#             # Resize to final size for thumbnail
#             x = circular_img.resize((107, 107), Image.LANCZOS)
#             print(f"Successfully processed profile image to circular format for queue")
#         except Exception as e:
#             print(f"Failed to process profile image for queue: {e}")
#             # Create a simple fallback circular profile image
#             x = Image.new("RGBA", (107, 107), (0, 0, 0, 0))
#             draw = ImageDraw.Draw(x)
#             # Nice blue circle with user icon
#             draw.ellipse([(2, 2), (105, 105)], fill="#3498DB", outline="#2980B9", width=2)
#             # Simple user icon
#             draw.ellipse([(35, 25), (72, 62)], fill="white")  # Head
#             draw.ellipse([(20, 65), (87, 132)], fill="white")  # Body
#             print("Created enhanced fallback circular profile image for queue")

#         try:
#             youtube = Image.open(f"cache/thumb{videoid}.png")
#             bg_path = "Dolbymusic/assets/anonx.png"
#             if os.path.exists(bg_path):
#                 bg = Image.open(bg_path)
#             else:
#                 bg = Image.new("RGBA", (1280, 720), color=(0, 0, 0, 180))
#         except Exception:
#             # Create fallback images
#             youtube = Image.new("RGB", (480, 360), color="gray")
#             bg = Image.new("RGBA", (1280, 720), color=(0, 0, 0, 180))

#         try:
#             image1 = changeImageSize(1280, 720, youtube)
#             image2 = image1.convert("RGBA")
#             background = image2.filter(filter=ImageFilter.BoxBlur(30))
#             enhancer = ImageEnhance.Brightness(background)
#             background = enhancer.enhance(0.6)

#             image3 = changeImageSize(1280, 720, bg)
#             image5 = image3.convert("RGBA")
#             Image.alpha_composite(background, image5).save(f"cache/temp{videoid}.png")
#         except Exception:
#             # Create a fallback composite
#             fallback = Image.new("RGBA", (1280, 720), color=(50, 50, 50, 255))
#             fallback.save(f"cache/temp{videoid}.png")

#         try:
#             Xcenter = youtube.width / 2
#             Ycenter = youtube.height / 2
#             x1 = Xcenter - 250
#             y1 = Ycenter - 250
#             x2 = Xcenter + 250
#             y2 = Ycenter + 250
#             logo = youtube.crop((x1, y1, x2, y2))
#             logo.thumbnail((520, 520), Image.LANCZOS)
#             logo.save(f"cache/chop{videoid}.png")
#             if not os.path.isfile(f"cache/cropped{videoid}.png"):
#                 im = Image.open(f"cache/chop{videoid}.png").convert("RGBA")
#                 add_corners(im)
#                 im.save(f"cache/cropped{videoid}.png")
#         except Exception:
#             # Create a fallback cropped image
#             fallback_crop = Image.new("RGBA", (365, 365), color=(100, 100, 100, 255))
#             fallback_crop.save(f"cache/cropped{videoid}.png")

#         try:
#             crop_img = Image.open(f"cache/cropped{videoid}.png")
#             logo = crop_img.convert("RGBA")
#             logo.thumbnail((365, 365), Image.LANCZOS)
#             width = int((1280 - 365) / 2)
#             background = Image.open(f"cache/temp{videoid}.png")
#             background.paste(logo, (width + 2, 138), mask=logo)
            
#             # Paste the profile image with proper handling
#             if x.mode != "RGBA":
#                 x = x.convert("RGBA")
#             background.paste(x, (710, 427), mask=x)
#             background.paste(image3, (0, 0), mask=image3)
#             print(f"Successfully composed final queue thumbnail with profile image")
#         except Exception as e:
#             print(f"Failed to compose final queue thumbnail: {e}")
#             # Create a fallback background
#             background = Image.new("RGBA", (1280, 720), color=(80, 80, 80, 255))

#         try:
#             draw = ImageDraw.Draw(background)
#             font_path = "Dolbymusic/assets/font2.ttf"
#             if os.path.exists(font_path):
#                 font = ImageFont.truetype(font_path, 45)
#                 arial = ImageFont.truetype(font_path, 30)
#             else:
#                 font = ImageFont.load_default()
#                 arial = ImageFont.load_default()
#         except Exception:
#             # Use default fonts
#             draw = ImageDraw.Draw(background)
#             font = ImageFont.load_default()
#             arial = ImageFont.load_default()
        
#         try:
#             para = textwrap.wrap(title, width=32)
#         except Exception:
#             para = ["Unknown Title"]
            
#         try:
#             draw.text(
#                 (455, 25),
#                 "ADDED TO QUEUE",
#                 fill="white",
#                 stroke_width=5,
#                 stroke_fill="black",
#                 font=font,
#             )
#             if len(para) > 0 and para[0]:
#                 bbox = draw.textbbox((0, 0), f"{para[0]}", font=font)
#                 text_w = bbox[2] - bbox[0]
#                 draw.text(
#                     ((1280 - text_w) / 2, 530),
#                     f"{para[0]}",
#                     fill="white",
#                     stroke_width=1,
#                     stroke_fill="white",
#                     font=font,
#                 )
#             if len(para) > 1 and para[1]:
#                 bbox = draw.textbbox((0, 0), f"{para[1]}", font=font)
#                 text_w = bbox[2] - bbox[0]
#                 draw.text(
#                     ((1280 - text_w) / 2, 580),
#                     f"{para[1]}",
#                     fill="white",
#                     stroke_width=1,
#                     stroke_fill="white",
#                     font=font,
#                 )
#         except Exception:
#             pass
            
#         try:
#             bbox = draw.textbbox((0, 0), f"Duration: {duration} Mins", font=arial)
#             text_w = bbox[2] - bbox[0]
#             draw.text(
#                 ((1280 - text_w) / 2, 660),
#                 f"Duration: {duration} Mins",
#                 fill="white",
#                 font=arial,
#             )
#         except Exception:
#             pass

#         try:
#             os.remove(f"cache/thumb{videoid}.png")
#         except:
#             pass
#         file = f"cache/que{videoid}_{user_id}.png"
#         background.save(f"cache/que{videoid}_{user_id}.png")
#         return f"cache/que{videoid}_{user_id}.png"
#     except Exception as e:
#         print(e)
#         return YOUTUBE_IMG_URL


# async def get_thumb(videoid, user_id):
#     """
#     Main thumbnail function that returns either cached or newly generated thumbnail
#     This is the function that other modules import and use
#     """
#     return await gen_thumb(videoid, user_id)


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

# ----------------- UTILS ---------------------

def changeImageSize(maxWidth, maxHeight, image):
    ratio = min(maxWidth / image.size[0], maxHeight / image.size[1])
    newWidth = int(image.size[0] * ratio)
    newHeight = int(image.size[1] * ratio)
    return image.resize((newWidth, newHeight), Image.LANCZOS)

def add_corners(im):
    mask = Image.new("L", im.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse([(0, 0), im.size], fill=255)
    im.putalpha(mask)

async def download_image(url, path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(path, mode="wb")
                await f.write(await resp.read())
                await f.close()
                return path
    return None

# ----------------- PROFILE PHOTO HANDLING ---------------------

async def get_circular_profile_image(user_id):
    os.makedirs("cache", exist_ok=True)
    img_path = f"cache/profile_{user_id}.png"

    # 1️⃣ Try to get user's photo
    try:
        photos = await app.get_profile_photos(user_id, limit=1)
        if photos.total_count > 0:
            file = await app.download_media(photos.photos[0][0], file_name=img_path)
            print(f"[PROFILE] Got user profile photo for {user_id}")
        else:
            raise Exception("No user photos")
    except Exception as e:
        print(f"[PROFILE] No user photo: {e}")
        # 2️⃣ Try bot photo
        try:
            bot_photos = await app.get_profile_photos(app.id, limit=1)
            if bot_photos.total_count > 0:
                file = await app.download_media(bot_photos.photos[0][0], file_name=img_path)
                print(f"[PROFILE] Using bot profile photo for {user_id}")
            else:
                raise Exception("No bot photos")
        except Exception as e2:
            print(f"[PROFILE] No bot photo: {e2}")
            # 3️⃣ Create fallback avatar
            img = Image.new("RGB", (640, 640), "#2C3E50")
            draw = ImageDraw.Draw(img)
            draw.ellipse([(50, 50), (590, 590)], fill="#3498DB", outline="#2980B9", width=10)
            draw.ellipse([(220,180), (420,380)], fill="#ECF0F1")
            draw.ellipse([(120,350), (520,750)], fill="#ECF0F1")
            img.save(img_path)
            print(f"[PROFILE] Created default avatar for {user_id}")

    # ➡️ Make circular
    im = Image.open(img_path).convert("RGBA").resize((640,640), Image.LANCZOS)
    mask = Image.new("L", (640,640), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse([(0,0), (640,640)], fill=255)
    circular_img = Image.new("RGBA", (640,640))
    circular_img.paste(im, (0,0), mask=mask)
    circular_img = circular_img.resize((107,107), Image.LANCZOS)
    final_path = f"cache/circular_{user_id}.png"
    circular_img.save(final_path)
    return final_path

# ----------------- MAIN THUMB GENERATOR ---------------------

async def gen_thumb(videoid, user_id):
    os.makedirs("cache", exist_ok=True)
    final_path = f"cache/{videoid}_{user_id}.png"
    if os.path.isfile(final_path):
        return final_path

    try:
        # -------- Get YouTube details
        results = VideosSearch(f"https://www.youtube.com/watch?v={videoid}", limit=1)
        result = (await results.next())["result"][0]
        title = re.sub("\W+", " ", result.get("title", "Unknown")).title()
        duration = result.get("duration", "Unknown")
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]
    except Exception:
        title, duration, thumbnail = "Unknown", "Unknown", None

    # -------- Download YouTube thumbnail
    thumb_path = f"cache/youtube_{videoid}.png"
    if thumbnail:
        await download_image(thumbnail, thumb_path)
    else:
        Image.new("RGB", (480, 360), "gray").save(thumb_path)

    # -------- Get circular user photo
    profile_path = await get_circular_profile_image(user_id)
    profile_img = Image.open(profile_path).convert("RGBA")

    # -------- Compose background
    youtube = Image.open(thumb_path)
    resized_bg = changeImageSize(1280, 720, youtube).convert("RGBA")
    blurred_bg = resized_bg.filter(ImageFilter.BoxBlur(30))
    enhancer = ImageEnhance.Brightness(blurred_bg)
    background = enhancer.enhance(0.6)

    # Optional overlay asset
    overlay_path = "Dolbymusic/assets/anonx.png"
    if os.path.exists(overlay_path):
        overlay = changeImageSize(1280,720, Image.open(overlay_path)).convert("RGBA")
        background = Image.alpha_composite(background, overlay)

    # -------- Crop logo
    center_x, center_y = youtube.width//2, youtube.height//2
    logo = youtube.crop((center_x-250, center_y-250, center_x+250, center_y+250))
    logo.thumbnail((365, 365), Image.LANCZOS)
    add_corners(logo)

    # -------- Paste everything
    bg = Image.new("RGBA", (1280,720))
    bg.paste(background, (0,0))
    bg.paste(logo, ((1280-365)//2,138), mask=logo)
    bg.paste(profile_img, (710,427), mask=profile_img)

    # -------- Add texts
    draw = ImageDraw.Draw(bg)
    font_path = "Dolbymusic/assets/font2.ttf"
    try:
        font = ImageFont.truetype(font_path, 45) if os.path.exists(font_path) else ImageFont.load_default()
        arial = ImageFont.truetype(font_path, 30) if os.path.exists(font_path) else ImageFont.load_default()
    except:
        font, arial = ImageFont.load_default(), ImageFont.load_default()

    para = textwrap.wrap(title, width=32)
    draw.text((450, 25), "STARTED PLAYING", fill="white", stroke_width=3, stroke_fill="grey", font=font)
    if len(para) > 0:
        bbox = draw.textbbox((0,0), para[0], font=font)
        draw.text(((1280-bbox[2])/2, 530), para[0], fill="white", stroke_width=1, stroke_fill="white", font=font)
    if len(para) > 1:
        bbox = draw.textbbox((0,0), para[1], font=font)
        draw.text(((1280-bbox[2])/2, 580), para[1], fill="white", stroke_width=1, stroke_fill="white", font=font)
    draw.text(((1280-200)//2, 660), f"Duration: {duration} Mins", fill="white", font=arial)

    # -------- Save & return
    bg.save(final_path)
    return final_path
