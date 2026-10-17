import os

from dotenv import load_dotenv

load_dotenv()

SUPPORTED_FORMATS = ('.mp3', '.wav', '.ogg', '.flac', '.m4a', '.opus')
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
PREFIX = os.getenv('DISCORD_BOT_PREFIX') or '/'
MUSIC_FOLDER = os.getenv('DISCORD_BOT_MUSIC_SOURCE_FOLDER') or "music"
DEBUG = (os.getenv('DISCORD_BOT_DEBUG') or '').lower() in ('1', 'true', 'yes')
DEFAULT_BITRATE = 96 # Opus kbps sent to Discord. Other options: 128 (higher quality), 64 (less traffic)
BITRATE = DEFAULT_BITRATE

_bitrate_setting = os.getenv('DISCORD_BOT_BITRATE')
if _bitrate_setting:
    if _bitrate_setting.isdigit() and 16 <= int(_bitrate_setting) <= 512:
        BITRATE = int(_bitrate_setting)
    else:
        print(f"DISCORD_BOT_BITRATE must be a number from 16 to 512, got '{_bitrate_setting}'. Using {DEFAULT_BITRATE}")
