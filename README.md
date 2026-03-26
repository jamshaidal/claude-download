# Video Downloader Web App

A web application for downloading videos from YouTube, Facebook, TikTok, Instagram, and other supported platforms.

## Features

- Download videos in multiple qualities
- Extract audio (MP3) from videos
- Modern, responsive UI
- Real-time video information preview

## Tech Stack

- **Backend**: Python, Flask, yt-dlp
- **Frontend**: React + Vite

## Prerequisites

### Backend
- Python 3.8+
- FFmpeg (for audio extraction)

### Frontend
- Node.js 16+

### Installing FFmpeg (for audio extraction)

**Windows:**
1. Download from https://ffmpeg.org/download.html
2. Extract and add `bin` folder to PATH
3. Verify: `ffmpeg -version`

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

## Setup & Running

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
python app.py
```

Backend will start on http://localhost:5000

### 2. Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will start on http://localhost:3000

### 3. Using the Application

1. Open http://localhost:3000 in your browser
2. Paste a video URL (YouTube, TikTok, Instagram, Facebook, etc.)
3. Click "Fetch Info" to see available options
4. Select quality or enable "Audio Only" for MP3
5. Click "Download" to save the file

## Project Structure

```
.
├── backend/
│   ├── app.py              # Flask server
│   ├── requirements.txt    # Python dependencies
│   └── downloads/          # Temporary storage (auto-created)
│
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── App.jsx         # Main app component
│   │   ├── api.js          # API service
│   │   └── index.css       # Styles
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/info` - Get video information
  ```json
  { "url": "https://youtube.com/watch?v=..." }
  ```
- `GET /api/download/<video_id>?url=<url>&format_id=<id>&audio_only=<bool>` - Download file

## Legal & Ethical Considerations

**Important**: This tool is for educational purposes only. You should only download videos that you own or have explicit permission to download. Downloading copyrighted content without authorization may violate Terms of Service and copyright laws.

## Troubleshooting

### "FFmpeg not found" error
- Ensure FFmpeg is installed and in your PATH
- Test: `ffmpeg -version` in terminal

### "Failed to extract video information"
- The URL might be invalid or behind age restriction
- Some platforms may block automated access
- Try with a different public video URL

### Backend returns 500
- Check if downloads/ folder exists and is writable
- Check Python dependencies: `pip install -r requirements.txt`

## Limitations

- Some platforms may employ anti-bot measures
- Videos may be unavailable due to privacy settings, age restrictions, or region locks
- Audio extraction requires FFmpeg
- Large files may take time to process

## License

This project is for educational purposes. No license - use at your own risk and in accordance with platform terms.