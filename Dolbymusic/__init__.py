from Dolbymusic.core.bot import AyushSolo
from Dolbymusic.core.dir import dirr
from Dolbymusic.core.git import git
from Dolbymusic.core.userbot import Userbot
from Dolbymusic.misc import dbb, heroku, sudo

from .logging import LOGGER

dirr()
git()
dbb()
heroku()
# sudo()

app = AyushSolo()
userbot = Userbot()


from .platforms import *

Carbon = CarbonAPI()
Spotify = SpotifyAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
