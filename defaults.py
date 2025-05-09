import logging
import os
import sys
from dotenv import load_dotenv

from enum import EnumType, Enum

# Load environment variables
#load_dotenv()


class LinkType(Enum):
	YOUTUBE = 1
	INSTAGRAM = 2


BOT_TOKEN = os.getenv("BOT_TOKEN")
LIMIT_SIZE = int(os.getenv("FILE_SIZE_LIMIT_BYTES"))
ADMINS_CHAT_ID = os.getenv("ADMINS_CHAT_ID").split(",")

# YouTube URL patterns
YOUTUBE_PATTERNS = [
	# Standard youtube.com links
	r'https?://(www\.)?youtube\.com/watch\?v=[\w-]+(\S*)',
	# Shortened youtu.be links
	r'https?://youtu\.be/[\w-]+(\S*)',
	# Mobile youtube.com links
	r'https?://m\.youtube\.com/watch\?v=[\w-]+(\S*)',
	# YouTube shorts
	r'https?://(www\.)?youtube\.com/shorts/[\w-]+(\S*)',
	# YouTube channel links
	r'https?://(www\.)?youtube\.com/channel/[\w-]+(\S*)',
	# YouTube user links
	r'https?://(www\.)?youtube\.com/user/[\w-]+(\S*)',
	# YouTube playlist links
	r'https?://(www\.)?youtube\.com/playlist\?list=[\w-]+(\S*)'
]
# Instagram URL patterns
INSTAGRAM_PATTERNS = [
	r'https?://(www\.)?instagram\.com/reel/[\w-]+(\S*)',
	r'https?://(www\.)?instagram\.com/p/[\w-]+(\S*)'
]

# Configure logging
logging.basicConfig(
	level=logging.DEBUG,
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	handlers=[
		logging.FileHandler("telegram_bot.log"),
		logging.StreamHandler()
	]
)
logger = logging.getLogger(__name__)

if not BOT_TOKEN:
	logger.error("No BOT_TOKEN found in .env file. Please add your bot token.")
	sys.exit(1)
