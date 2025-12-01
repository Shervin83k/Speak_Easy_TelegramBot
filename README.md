# TTV Bot v2

A Telegram bot for text-to-speech conversion, batch audio processing, and seamless multi-language support. Designed for efficiency, reliability, and extensibility.

### Real-Time TTS Conversion
*Convert text messages into audio on the fly with support for multiple languages and voice speeds.*

### Batch Processing
*Send multiple text lines at once and receive generated audio files automatically.*

### Multi-Language Support
*English, Farsi, and easy extension to additional languages.*

### Robust & Secure
*Rate-limiting, input validation, and session handling ensure the bot remains safe under heavy usage.*

## Features

### Core
- Telegram bot interface (python-telegram-bot v20)
- Real-time text-to-speech (gTTS + pydub)
- Audio file management and cleanup
- Language selection per user

### Middleware
- Rate limiter to prevent abuse
- Input sanitization and filename validation

### Data Management
- SQLite storage for session and usage tracking
- Temporary audio storage with automatic cleanup
- Usage quota enforcement (daily limits)

### Development & Testing
- Async/await architecture for responsiveness
- Comprehensive pytest suite covering handlers, TTS, quotas, and integration
- Logging for debugging and monitoring

## Installation

### Prerequisites
- Python 3.8+
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- FFMPEG installed (included in `src/ffmpeg`)

### Project Structure
TTV_bot_version2/
├── src/
│   ├── bot.py                 # Bot entry point
│   ├── config/                # Constants and configuration
│   ├── ffmpeg/                # Bundled ffmpeg binaries & docs
│   ├── handlers/              # Telegram message handlers
│   ├── locales/               # Multi-language JSON files
│   ├── middleware/            # Rate limiting & security
│   ├── models/                # User sessions and quota models
│   ├── services/              # TTS, File, Cache, Quota services
│   └── utils/                 # Logger, validators, helpers
├── data/                      # Bot database & temp audio
├── logs/                      # Bot & admin logs
├── tests/                     # Full pytest suite
├── requirements.txt           # Dependencies
└── install_ffmpeg.bat         # Setup script for Windows

### Quick Setup
```bash
git clone https://github.com/Shervin83k/TTV_bot_version2
cd TTV_bot_version2/src
python -m venv venv
# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
pip install -r ../requirements.txt
