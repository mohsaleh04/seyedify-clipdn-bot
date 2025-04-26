# Seyedify Clip Downloader

A Telegram bot that automatically detects YouTube links in group chats and downloads them for easy viewing. This bot is designed to help users easily save and share YouTube content within Telegram groups without leaving the platform.

## Features

- 🔍 Monitors Telegram group messages for YouTube links
- 🎬 Downloads videos in optimal quality (480p MP4)
- 🔗 Supports various YouTube URL formats:
  - Standard youtube.com links
  - Shortened youtu.be links
  - Mobile youtube.com links
  - YouTube Shorts
  - YouTube channel links
  - YouTube user links
  - YouTube playlist links
- 📏 Enforces configurable file size limits to comply with Telegram restrictions
- 🔊 Automatic audio-video merging capabilities for formats that require it
- ⚡ Uses yt-dlp for efficient and reliable downloading
- 📤 Sends downloaded videos directly in the chat as a reply to the original message

## Requirements

- Python 3.6+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- FFmpeg (for audio-video merging)
- The following Python packages:
  - pytelegrambotapi
  - yt-dlp
  - requests
  - python-dotenv

## Installation and Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/seyedify-clip-downloader.git
   cd seyedify-clip-downloader
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On Unix or MacOS
   source .venv/bin/activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Install FFmpeg:
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - Linux: `sudo apt-get install ffmpeg`
   - macOS: `brew install ffmpeg`

5. Create a `.env` file in the project root with your configuration (see Environment Variables section)

## Environment Variables

Create a `.env` file in the project root with the following variables:

```
BOT_TOKEN=your_telegram_bot_token
FILE_SIZE_LIMIT_BYTES=50000000  # Default: 50MB
```

## Usage

1. Start the bot:
   ```bash
   python main.py
   ```

2. Add the bot to your Telegram group

3. Send YouTube links in the group chat

4. The bot will automatically:
   - Detect YouTube links
   - Download the video in optimal quality
   - Reply to the original message with the downloaded video

## How it Works

1. The bot monitors all messages in groups where it's added
2. When a YouTube link is detected, it extracts the URL
3. The ClipProcessor class handles downloading the video:
   - Selects optimal format (480p MP4)
   - Downloads the video content
   - If needed, downloads audio separately and merges it with FFmpeg
   - Sends the final video back to the Telegram group

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

