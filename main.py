#!/usr/bin/env python
import os
import signal
import sys
from datetime import datetime

import telebot

from defaults import logger, BOT_TOKEN, LinkType, ADMINS_CHAT_ID
from processing.clip import ClipProcessor
from utils import is_link_from_seyed_ecosystem_groups, is_message_contains_a_social_link, extract_social_links_from_text

try:
	bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
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


@bot.message_handler(func=lambda message: message.chat.type == 'private')
def handle_im_up_message(message):
	if str(message.chat.id) in ADMINS_CHAT_ID:
		bot.reply_to(message, "من دارم کار میکنم!! 🎁🎁🎁")


@bot.message_handler(func=lambda message: message.chat.type in ['group', 'supergroup'])
def handle_group_message(message):
	try:
		if not message.text:
			return
		logger.info(
			f"Message received in group {message.chat.title} from {message.from_user.username or message.from_user.first_name}")

		if is_message_contains_a_social_link(message.text):
			if not is_link_from_seyed_ecosystem_groups(message.chat.title):
				bot.reply_to(message, "این چت جزو چت های دربار سید نمی باشد! ⛔")
				return

			link_type, links = extract_social_links_from_text(message.text)
			logger.info(f"YouTube/Instagram(Social) link(s) detected: {links}")

			if not links:
				bot.reply_to(message, "این چیه فرستادی؟\nلینک ارسالی نامعتبره! 😒")
				return

			for link in links:
				process_social_link(message, link, link_type)

	except Exception as e:
		logger.error(f"Error handling message: {e}")


def process_social_link(message, link: str, link_type: str):
	logger.info("Social link processing placeholder - to be implemented")
	doing_work_msg = "دارم رو لینکایی که فرستادین کار میکنم ...\n🔍🤖😊\n\n"
	replied_message = bot.reply_to(message, doing_work_msg)
	update_status_log_message = lambda log_message: bot.edit_message_text(message_id=replied_message.message_id,
	                                                                      chat_id=replied_message.chat.id,
	                                                                      text=doing_work_msg + str(log_message))
	clip_downloader = ClipProcessor(link)
	if link_type == LinkType.YOUTUBE.value:
		result = clip_downloader.process_youtube_clip(update_status_log_message)
	elif link_type == LinkType.INSTAGRAM.value:
		result = clip_downloader.process_instagram_clip(update_status_log_message)
	else:
		bot.reply_to(message, f"لینک ارسالی پشتیبانی نمیشه! 😥")
		bot.delete_message(chat_id=message.chat.id, message_id=replied_message.message_id)
		return

	if result["status"] == "success":
		try:
			# Use the exact video path from the download operation
			video_path = result["video_path"]
			image_path = result["image_path"]

			if video_path:
				if not os.path.exists(video_path):
					bot.reply_to(message, f"حین آپلود فایل، فایل گم شد! 🥲⚠️")
					bot.delete_message(chat_id=message.chat.id, message_id=replied_message.message_id)
					return
				with open(video_path, 'rb') as video:
					bot.send_video(chat_id=message.chat.id, video=video, timeout=1200,
					               reply_to_message_id=message.message_id,
					               caption="بفرمایید . اینم ویدئو درخواستی... 🎁")
				os.remove(video_path)
				logger.info(f"Video uploaded: {video_path}")
			elif image_path:
				if not os.path.exists(image_path):
					bot.reply_to(message, f"حین آپلود فایل، فایل گم شد! 🥲⚠️")
					bot.delete_message(chat_id=message.chat.id, message_id=replied_message.message_id)
					return
				with open(image_path, 'rb') as image:
					bot.send_photo(chat_id=message.chat.id, photo=image, timeout=1200,
					               reply_to_message_id=message.message_id,
					               caption="بفرمایید . اینم تصویر درخواستی... 🎁")
				os.remove(image_path)
				logger.info(f"Image uploaded: {image_path}")
		except Exception as eis:
			logger.error(f"Error uploading or deleting video: {eis}")
			bot.reply_to(message, f"❌ خطایی حین آپلود یا حذف فایل: {str(eis)}")
	elif result["status"] == "error":
		logger.error(f"Error while processing file: {result['msg']}")
		bot.reply_to(message, f"❌ خطایی حین پردازش فایل: {result['msg']}")
	bot.delete_message(chat_id=message.chat.id, message_id=replied_message.message_id)


if __name__ == "__main__":
	try:
		# Setup graceful shutdown
		setup_graceful_shutdown()

		# Log bot start
		logger.info(f"Starting Bot at {datetime.now().isoformat()}")

		# Start the bot
		logger.info("Bot is now polling for incoming messages...")
		bot.polling(none_stop=True, interval=0, timeout=60)

	except Exception as e:
		logger.error(f"Critical error: {e}")
		sys.exit(1)
