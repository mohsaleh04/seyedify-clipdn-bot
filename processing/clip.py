import logging
import os
import subprocess as s
import time

from instaloader import Instaloader
from yt_dlp import YoutubeDL, DownloadError
from yt_dlp.compat import shutil

from defaults import logger, LIMIT_SIZE


class ClipProcessor:
	url: str
	L: Instaloader

	def __init__(self, url):
		self.url = url
		self.L = Instaloader()

	def process_youtube_clip(self, message_log_updater) -> dict:
		url = self.url.strip()
		status_log_header_text = "<b>وضعیت:</b>\n"
		message_log_updater(status_log_header_text + "در حال دریافت فرمت های فیلم")
		try:
			process = s.Popen(['yt-dlp', '--list-formats', url], stdout=s.PIPE, stderr=s.PIPE)
			stdout, stderr = process.communicate()
			formats_output = stdout.decode('utf-8')
			logger.debug(formats_output)
		except Exception as e:
			return {"status": "error", "msg": f"ناتوانی در دریافت فرمت ها: {e}"}

		# Extract video information
		ydl_opts = {'quiet': True, 'no_warnings': True}

		try:
			with YoutubeDL(ydl_opts) as ydl:
				info = ydl.extract_info(url, download=False)
				formats = info.get('formats', [])
		except DownloadError as de:
			return {"status": "error", "msg": f"ناتوانی در دانلود: {de}"}

		###############

		message_log_updater(status_log_header_text + "در حال انتخاب بهینه ترین فرمت فیلم")
		selected_format = None
		# For speedy downloading ... (audio & video both)
		# for i, fmt in enumerate(formats):
		# 	audio_codec = fmt.get('acodec', 'None')
		# 	video_codec = fmt.get('vcodec', 'None')
		# 	filesize = fmt.get('filesize') or fmt.get('filesize_approx')
		#
		# 	if str(audio_codec).lower() != "none" and str(video_codec).lower() != "none":
		# 		if filesize:
		# 			if filesize <= LIMIT_SIZE:
		# 				selected_format = fmt
		# 				break
		# 			else:
		# 				return {"status": "error", "msg": "file size limit exceeded"}

		for i, fmt in enumerate(formats):
			resolution = fmt.get('resolution', 'Audio Only') if fmt.get('vcodec') != 'none' else 'Audio Only'
			file_extension = fmt.get('ext', 'Unknown')
			# audio_codec = fmt.get('acodec', 'None')
			video_codec = fmt.get('vcodec', 'None')
			file_size = fmt.get('filesize') or fmt.get('filesize_approx')

			if str(video_codec).lower() != "none":
				if file_size:
					if file_size <= LIMIT_SIZE:
						if str(video_codec).startswith("avc1") and str(resolution).startswith("480x") and str(
								file_extension) == "mp4":
							selected_format = fmt
							break
					else:
						return {"status": "error", "msg": "حجم فایل خیلی زیاده!"}

		if selected_format is None:
			return {"status": "error", "msg": "هیچ فرمت مناسبی برای دانلود وجود نداشت."}

		selected_format_id = selected_format['format_id']
		has_audio = selected_format.get('acodec') != 'none'
		has_video = selected_format.get('vcodec') != 'none'

		# Handle audio separately if not present in selected format
		audio_downloaded = False
		audio_path = None
		if has_video and not has_audio:
			message_log_updater(status_log_header_text + "در حال دانلود کانال صوتی فیلم ...")

			logging.debug("Selected format has NO AUDIO. Attempting to download audio separately...")
			try:
				audio_destination = os.getcwd() + '/audio_temp'
				os.makedirs(audio_destination, exist_ok=True)
				audio_filename = os.path.join(audio_destination, '%(title)s.%(ext)s')
				s.call(['yt-dlp', '-x', '--audio-format', 'mp3', '-o', audio_filename, url])

				# Locate the downloaded audio file
				for root, _, files in os.walk(audio_destination):
					for file in files:
						if file.endswith(".mp3"):
							audio_path = os.path.join(root, file)
							break

				if not audio_path or not os.path.exists(audio_path):
					logging.error(
						f"Error: Audio file not found in {audio_destination}. Please check if the file was downloaded correctly.")
					return {"status": "error", "msg": f"عدم توانایی تحلیل فایل صوتی"}

				logging.debug("MP3 audio downloaded successfully.")
				audio_downloaded = True
			except Exception as err:
				logging.error(f"Error downloading MP3 audio: {err}")
				return {"status": "error", "msg": "ناتوانی در دانلود فایل صوتی"}

		#################

		message_log_updater(status_log_header_text + "در حال دانلود خودِ فیلم ...")
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
			return {"status": "error", "msg": f"ناتوانی در دانلود فیلم: {di}"}

		time2 = int(time.time())
		ftime = time2 - time1
		logger.info(f"Time taken to download: {ftime} sec")
		message_log_updater(status_log_header_text + f"دانلود فیلم {ftime} ثانیه طول کشید.")


		# Merge audio and video if necessary
		if has_video and not has_audio:
			if audio_downloaded:
				message_log_updater(status_log_header_text + "در حال ادغام سازی تصویر و صوت")
				logging.debug("Merging audio and video...")
				merged_path = os.path.join(destination, f"{info['title']}_merged.mp4")
				try:
					# Add timeout to prevent hanging
					ffmpeg_command = ['ffmpeg', '-y',  # Overwrite output files without asking
					                  '-i', video_path, '-i', audio_path, '-c:v', 'copy', '-c:a', 'aac', merged_path, ]
					logging.debug(f"Executing: {' '.join(ffmpeg_command)}")

					# Use subprocess to execute the command and capture output
					process = s.Popen(ffmpeg_command, stdout=s.PIPE, stderr=s.PIPE, text=True)
					stdout, stderr = process.communicate(timeout=300)  # Timeout after 5 minutes

					# Check return code
					if process.returncode == 0:
						logging.debug("Audio and video merged successfully.")
						os.remove(video_path)
						os.remove(audio_path)
					else:
						logger.error(f"Error on merging video and audio; ffmpeg stdout: {stdout}")
						return {"status": "error", "msg": f"خطا در حین ادغام فیلم و صوت: {stderr}"}
				except s.TimeoutExpired:
					process.kill()
					return {"status": "error",
					        "msg": "فرایند ادغام سازی، بیش از حد طول کشید و عملیات لغو شد."}
				except Exception as e:
					return {"status": "error", "msg": f"خطا در حین ادغام فیلم و صوت: {e}"}
			else:
				return {"status": "error", "msg": f"نتوانست فایل صدا را دانلود و با فیلم ادغام کند!"}
		else:
			merged_path = video_path

		message_log_updater(status_log_header_text + "در حال پاکسازی فایل های اضافی")
		# Cleanup temporary files
		temp_audio_dir = os.getcwd() + '/audio_temp'
		if os.path.exists(temp_audio_dir):
			shutil.rmtree(temp_audio_dir, ignore_errors=True)
			logger.info("Temporary audio files cleaned up.")

		logger.info("downloading operation ends up")
		message_log_updater(status_log_header_text + "فرایند دانلود تمام شد؛ ✅\nدر حال آپلود فیلم... ")

		if has_video and not has_audio:
			return {"status": "success", "msg": None, "video_path": merged_path, "image_path": None}
		else:
			return {"status": "success", "msg": None, "video_path": video_path, "image_path": None}

	def process_instagram_clip(self, message_log_updater) -> dict:
		url = self.url.strip().split("?")[0]
		status_log_header_text = "<b>وضعیت:</b>\n"
		message_log_updater(status_log_header_text + "در حال بررسی لینک فیلم ..")

		if url.endswith("/"):
			url = url[:-1]  # Deleting last slash
		url_segments = url.split("/")
		post_type = url_segments[-2]

		if post_type not in ["reel", "p", "post", "r"]:
			return {"status": "error", "msg": "لینک نامعتبره!"}

		shortcode = url_segments[-1]

		##########################

		message_log_updater(status_log_header_text + "در حال دانلود فیلم ..")

		try:
			process = s.Popen(['instaloader', '--', f'-{shortcode}'], stdout=s.PIPE, stderr=s.PIPE)
			stdout, stderr = process.communicate()
			download_result = stdout.decode('utf-8')
			downloaded_folder = download_result.split()
			video_path = list(filter(lambda filename: filename.endswith(".mp4"), downloaded_folder))
			if video_path:
				video_path = video_path[0]
			cover_image_path = list(filter(lambda filename: filename.endswith(".jpg"), downloaded_folder))
			if cover_image_path:
				cover_image_path = cover_image_path[0]
		except Exception as e:
			return {"status": "error", "msg": f"خطایی حین دانلود فیلم: {e}"}

		message_log_updater(status_log_header_text + "فیلم دانلود شد؛ ✅\nدرحال بررسی و آپلود فیلم ...")

		#######################

		if video_path:
			video_path = os.path.join(os.getcwd(), video_path)
			return {"status": "success", "msg": None, "video_path": video_path, "image_path": None}
		elif cover_image_path:
			cover_image_path = os.path.join(os.getcwd(), cover_image_path)
			return {"status": "success", "msg": None, "image_path": cover_image_path}
		else:
			return {"status": "error", "msg": "لینکی که فرستادید، هیچی توش نیس! 😥"}
