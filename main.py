#!/usr/bin/env python
import os
import signal
import sys

import telebot

from datetime import datetime

from defaults import logger, BOT_TOKEN
from processing.clip import ClipProcessor
from utils import is_link_from_seyed_ecosystem, is_link_a_youtube_link, extract_youtube_links_from_text


try:
	bot = telebot.TeleBot(BOT_TOKEN)
	logger.info("Bot initialized successfully")
except Exception as e:
	logger.error(f"Failed to initialize bot: {e}")
	sys.exit(1)


def setup_graceful_shutdown():
	def signal_handler(sig, frame):
		logger.info("Shutdown signal received. Stopping bot...")
		bot.stop_polling()
		sys.exit(0)

	# Register signal handlers
	signal.signal(signal.SIGINT, signal_handler)
	signal.signal(signal.SIGTERM, signal_handler)


@bot.message_handler(func=lambda message: message.chat.type in ['group', 'supergroup'])
def handle_group_message(message):
	try:
		# Check if the message contains text
		if not message.text:
			return

		# Log basic message info
		logger.info(
			f"Message received in group {message.chat.title} from {message.from_user.username or message.from_user.first_name}")

		# Check for YouTube links
		if not is_link_from_seyed_ecosystem(message.chat.title):
			bot.reply_to(message, "Your chat is not part of the SEYED ecosystem.")
			return

		if is_link_a_youtube_link(message.text):
			links = extract_youtube_links_from_text(message.text)
			logger.info(f"YouTube link(s) detected: {links}")

			for link in links:
				process_youtube_link(message, link)
	except Exception as e:
		logger.error(f"Error handling message: {e}")


def process_youtube_link(message, link):
	# Placeholder for future implementation
	logger.info("YouTube link processing placeholder - to be implemented")
	replied_message = bot.reply_to(message, "Processing YouTube links ...")
	clip_downloader = ClipProcessor(link)
	result = clip_downloader.process_youtube_clip()
	bot.delete_message(chat_id=message.chat.id, message_id=replied_message.message_id)
	if result["status"] == "success":
		try:
			# Use the exact video path from the download operation
			video_path = result["video_path"]

			# Verify the file exists
			if not os.path.exists(video_path):
				bot.reply_to(message, f"Error processing video: File Not Found . After file parsing....")
				return

			# Upload the video to the group
			with open(video_path, 'rb') as video:
				bot.send_video(chat_id=message.chat.id, video=video, timeout=1200, reply_to_message_id=message.message_id)

			# Remove the file after successful upload
			os.remove(video_path)
			logger.info(f"Video uploaded and deleted: {video_path}")
		except Exception as eis:
			logger.error(f"Error uploading or deleting video: {eis}")
			bot.reply_to(message, f"Error processing video: {str(eis)}")
	elif result["status"] == "error":
		bot.reply_to(message, result["msg"])



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
