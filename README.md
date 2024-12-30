# Telegram Voice-to-Text Bot

A Telegram bot that converts voice messages to text using OpenAI's Whisper model and Firebase for data storage.

## Features

- Voice message to text conversion
- Firebase integration for data storage
- Cost-efficient implementation
- Support for multiple languages
- User-friendly interface

## Prerequisites

- Python 3.8+
- FFmpeg installed on your system
- Telegram Bot Token
- Firebase service account credentials

## Installation

1. Clone this repository:
```bash
git clone <your-repository-url>
cd voice-to-text-bot
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Install FFmpeg (if not already installed):
- Windows: Download from https://ffmpeg.org/download.html
- Linux: `sudo apt-get install ffmpeg`
- macOS: `brew install ffmpeg`

4. Set up your environment:
- Create a new bot with [@BotFather](https://t.me/botfather) on Telegram
- Set up a Firebase project and download the service account key
- Rename your service account key to `serviceAccountKey.json`
- Update `bot.py` with your Telegram bot token and Firebase database URL

## Configuration

1. Place your `serviceAccountKey.json` in the project root directory
2. Update the following in `bot.py`:
   - Replace 'YOUR_BOT_TOKEN' with your Telegram bot token
   - Replace 'YOUR_FIREBASE_DATABASE_URL' with your Firebase database URL

## Usage

1. Start the bot:
```bash
python bot.py
```

2. In Telegram:
   - Start a chat with your bot
   - Send a voice message
   - Wait for the transcription

## Cost Analysis

- Whisper API: Free (using local model)
- Firebase Spark Plan: Free
- Server hosting: ~$3/month (Digital Ocean/AWS Lightsail)
- Total monthly cost: ~$3

## Monetization

The bot can be monetized through:
- Premium features
- Usage limits for free tier
- Non-intrusive advertisements
- Subscription model

## Maintenance

- Regularly check Firebase usage limits
- Monitor server resources
- Update dependencies as needed
- Backup transcription data periodically

## License

MIT License
