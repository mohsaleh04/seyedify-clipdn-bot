#!/usr/bin/env python
"""
Telegram Bot for YouTube Link Detection

This bot monitors messages in Telegram groups and detects YouTube links.
It is designed with a modular architecture to allow for easy extension of functionality.
"""

import logging
import os
import re
import signal
import subprocess as s
import sys
import time
from datetime import datetime

import telebot
from dotenv import load_dotenv
from yt_dlp import YoutubeDL, DownloadError
from yt_dlp.compat import shutil

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

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
LIMIT_SIZE = int(os.getenv("FILE_SIZE_LIMIT_BYTES"))

# Check if token is available
if not BOT_TOKEN:
	logger.error("No BOT_TOKEN found in .env file. Please add your bot token.")
	sys.exit(1)

# Initialize the bot
try:
	bot = telebot.TeleBot(BOT_TOKEN)
	logger.info("Bot initialized successfully")
except Exception as e:
	logger.error(f"Failed to initialize bot: {e}")
	sys.exit(1)

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


class ClipProcessor:
	url: str

	def __init__(self, url):
		self.url = url

	def process_youtube_clip(self) -> dict:
		url = self.url.strip()
		try:
			process = s.Popen(['yt-dlp', '--list-formats', url], stdout=s.PIPE, stderr=s.PIPE)
			stdout, stderr = process.communicate()
			formats_output = stdout.decode('utf-8')
			logger.debug(formats_output)
		except Exception as e:
			return {"status": "error", "msg": f"Error listing formats: {e}"}

		# Extract video information
		ydl_opts = {'quiet': True, 'no_warnings': True, }

		try:
			with YoutubeDL(ydl_opts) as ydl:
				info = ydl.extract_info(url, download=False)
				formats = info.get('formats', [])
		except DownloadError as de:
			return {"status": "error", "msg": f"Failed to download: {de}"}

		###############

		selected_format = None
		# Display available formats with download size
		for i, fmt in enumerate(formats):
			audio_codec = fmt.get('acodec', 'None')
			video_codec = fmt.get('vcodec', 'None')
			filesize = fmt.get('filesize') or fmt.get('filesize_approx')

			if str(audio_codec).lower() != "none" and str(video_codec).lower() != "none":
				if filesize:
					if filesize <= LIMIT_SIZE:
						selected_format = fmt
						break
					else:
						return {"status": "error", "msg": "file size limit exceeded"}

		if selected_format is None:
			return {"status": "error", "msg": "no suitable format found for download"}

		selected_format_id = selected_format['format_id']

		# Handle audio separately if not present in selected format

		#################

		logger.info("Starting Video Download...")
		time1 = int(time.time())

		# Define download path
		destination = os.getcwd()

		if destination.__contains__("\\"):
			destination = destination.replace("\\", "/")

		video_path = os.path.join(destination, f"{info['title']}.mp4")
		ydl_opts = {'format': selected_format_id, 'outtmpl': video_path, }

		try:
			with YoutubeDL(ydl_opts) as ydl:
				ydl.download([url])
			logger.info("File downloaded")
		except Exception as di:
			return {"status": "error", "msg": f"Failed to download: {di}"}

		time2 = int(time.time())
		ftime = time2 - time1
		logger.info(f"Time taken to download: {ftime} sec")

		# Merge audio and video if necessary

		# Cleanup temporary files
		temp_audio_dir = os.getcwd() + '/audio_temp'
		if os.path.exists(temp_audio_dir):
			shutil.rmtree(temp_audio_dir, ignore_errors=True)
			logger.info("Temporary audio files cleaned up.")

		logger.info("downloading operation ends up")

		return {"status": "success", "msg": None, "video_path": video_path}


def is_youtube_link(text):
	"""
    Check if the given text contains a YouTube link.

    Args:
        text (str): The text to check for YouTube links.

    Returns:
        bool: True if a YouTube link is found, False otherwise.
    """
	for pattern in YOUTUBE_PATTERNS:
		if re.search(pattern, text):
			return True
	return False


def extract_youtube_links(text):
	"""
    Extract all YouTube links from the given text.

    Args:
        text (str): The text to extract YouTube links from.

    Returns:
        list: A list of extracted YouTube links.
    """
	links = []
	for pattern in YOUTUBE_PATTERNS:
		matches = re.finditer(pattern, text)
		for match in matches:
			links.append(match.group(0))
	return links


def is_from_seyed_ecosystem(title) -> bool:
	seyed_keywords = ["سید", "فرندز", "رفقا"]
	for keyword in seyed_keywords:
		if keyword in title.lower():
			return True
	return False


@bot.message_handler(func=lambda message: message.chat.type in ['group', 'supergroup'])
def handle_group_message(message):
	"""
    Handle messages sent in Telegram groups.

    Args:
        message (telebot.types.Message): The message object from Telegram.
    """
	try:
		# Check if the message contains text
		if not message.text:
			return

		# Log basic message info
		logger.info(
			f"Message received in group {message.chat.title} from {message.from_user.username or message.from_user.first_name}")

		# Check for YouTube links
		if not is_from_seyed_ecosystem(message.chat.title):
			bot.reply_to(message, "your chat is not part of the **SEYED** ecosystem.")
		if is_youtube_link(message.text):
			links = extract_youtube_links(message.text)
			logger.info(f"YouTube link(s) detected: {links}")

			for link in links:
				process_youtube_link(message, link)


	except Exception as e:
		logger.error(f"Error handling message: {e}")


def process_youtube_link(message, link):
	"""
    Process the detected YouTube links.
    This is a placeholder function for future implementation.

    Args:
        message (telebot.types.Message): The message object from Telegram.
        link (str): The list of YouTube links detected in the message.
    """
	# Placeholder for future implementation
	logger.info("YouTube link processing placeholder - to be implemented")
	bot.reply_to(message, "Processing YouTube links")
	clip_downloader = ClipProcessor(link)
	result = clip_downloader.process_youtube_clip()
	if result["status"] == "success":
		try:
			# Use the exact video path from the download operation
			video_path = result["video_path"]

			# Verify the file exists
			if not os.path.exists(video_path):
				raise FileNotFoundError(f"Downloaded video file not found at {video_path}")

			# Upload the video to the group
			with open(video_path, 'rb') as video:
				bot.send_video(chat_id=message.chat.id, video=video, timeout=1200)
				bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

			# Remove the file after successful upload
			os.remove(video_path)
			logger.info(f"Video uploaded and deleted: {video_path}")
		except Exception as eis:
			logger.error(f"Error uploading or deleting video: {eis}")
			bot.reply_to(message, f"Error processing video: {str(eis)}")
	elif result["status"] == "error":
		bot.reply_to(message, result["msg"])


def setup_graceful_shutdown():
	"""
    Set up signal handlers for graceful shutdown.
    """

	def signal_handler(sig, frame):
		logger.info("Shutdown signal received. Stopping bot...")
		bot.stop_polling()
		sys.exit(0)

	# Register signal handlers
	signal.signal(signal.SIGINT, signal_handler)
	signal.signal(signal.SIGTERM, signal_handler)


if __name__ == "__main__":
	try:
		# Setup graceful shutdown
		setup_graceful_shutdown()

		# Log bot start
		logger.info(f"Starting YouTube Link Bot at {datetime.now().isoformat()}")

		# Start the bot
		logger.info("Bot is now polling for messages...")
		bot.polling(none_stop=True, interval=0, timeout=60)

	except Exception as e:
		logger.error(f"Critical error: {e}")
		sys.exit(1)
