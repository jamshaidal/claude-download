import os
import uuid
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_file, Response, stream_with_context, send_from_directory
from flask_cors import CORS
import yt_dlp

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
CORS(app)

# Configuration
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
MAX_FILE_AGE_HOURS = 2
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


def cleanup_old_files():
    """Remove download files older than MAX_FILE_AGE_HOURS"""
    try:
        cutoff = datetime.now() - timedelta(hours=MAX_FILE_AGE_HOURS)
        for filename in os.listdir(DOWNLOAD_FOLDER):
            filepath = os.path.join(DOWNLOAD_FOLDER, filename)
            if os.path.isfile(filepath):
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                if file_time < cutoff:
                    os.remove(filepath)
                    print(f"Cleaned up old file: {filename}")
    except Exception as e:
        print(f"Cleanup error: {e}")


def get_video_info(url):
    """Extract video information using yt-dlp"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'skip_download': True,
        'no_check_certificate': True,
        'ignoreerrors': True,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            if info is None:
                return None, "Failed to extract video information"

            # Extract formats
            formats = []
            seen_qualities = set()

            for fmt in info.get('formats', []):
                # Skip audio-only formats for video selection (we'll handle separately)
                if fmt.get('vcodec') == 'none' and fmt.get('acodec') != 'none':
                    continue

                height = fmt.get('height')
                width = fmt.get('width')
                filesize = fmt.get('filesize') or fmt.get('filesize_approx')
                ext = fmt.get('ext', 'mp4')
                format_id = fmt.get('format_id', '')

                # Create quality label
                quality_label = None
                if height:
                    quality_label = f"{height}p"
                elif width:
                    quality_label = f"{width}x"
                else:
                    quality_label = "Best"

                # Avoid duplicates
                if quality_label and quality_label not in seen_qualities:
                    seen_qualities.add(quality_label)
                    formats.append({
                        'quality': quality_label,
                        'format_id': format_id,
                        'ext': ext,
                        'filesize': filesize,
                        'filesize_mb': round(filesize / (1024*1024), 2) if filesize else None,
                        'vcodec': fmt.get('vcodec'),
                        'acodec': fmt.get('acodec'),
                    })

            # Add audio-only format
            audio_formats = []
            for fmt in info.get('formats', []):
                if fmt.get('vcodec') == 'none' and fmt.get('acodec') != 'none':
                    ext = fmt.get('ext', 'm4a')
                    audio_formats.append({
                        'quality': f"Audio ({ext})",
                        'format_id': fmt.get('format_id'),
                        'ext': ext,
                        'filesize': fmt.get('filesize') or fmt.get('filesize_approx'),
                        'filesize_mb': round((fmt.get('filesize') or fmt.get('filesize_approx') or 0) / (1024*1024), 2) if (fmt.get('filesize') or fmt.get('filesize_approx')) else None,
                        'type': 'audio'
                    })

            # Sort formats by quality (height)
            formats.sort(key=lambda x: int(x['quality'].replace('p', '')) if x['quality'].endswith('p') else 0, reverse=True)

            # Add best audio option separately if not in formats
            if audio_formats:
                formats.extend(audio_formats[:1])

            return {
                'title': info.get('title', 'Unknown Title'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration'),
                'duration_str': f"{info.get('duration', 0) // 60}:{info.get('duration', 0) % 60:02d}" if info.get('duration') else None,
                'formats': formats,
                'uploader': info.get('uploader'),
                'platform': info.get('extractor_key'),
            }, None

    except Exception as e:
        return None, str(e)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})


@app.route('/api/info', methods=['POST'])
def get_info():
    """Get video information"""
    data = request.get_json()
    url = data.get('url', '').strip()

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    # Basic URL validation
    if not url.startswith(('http://', 'https://')):
        return jsonify({'error': 'Invalid URL format'}), 400

    # Run cleanup periodically
    cleanup_old_files()

    video_info, error = get_video_info(url)

    if error:
        return jsonify({'error': error}), 400

    if not video_info:
        return jsonify({'error': 'No video information found'}), 404

    return jsonify(video_info)


@app.route('/api/download/<video_id>', methods=['GET'])
def download_video(video_id):
    """Download video or audio"""
    format_id = request.args.get('format_id')
    audio_only = request.args.get('audio_only', 'false').lower() == 'true'
    url = request.args.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    # Generate unique filename
    unique_id = str(uuid.uuid4())[:8]
    timestamp = int(time.time())

    # yt-dlp options
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'no_check_certificate': True,
        'ignoreerrors': True,
        'noplaylist': True,
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, f'{unique_id}_{timestamp}.%(ext)s'),
    }

    # Configure format selection
    if audio_only:
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    elif format_id:
        ydl_opts['format'] = format_id
    else:
        ydl_opts['format'] = 'best'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_filename = ydl.prepare_filename(info)

            # Handle audio postprocessing extension change
            if audio_only and os.path.exists(downloaded_filename):
                downloaded_filename = downloaded_filename.rsplit('.', 1)[0] + '.mp3'

            if not os.path.exists(downloaded_filename):
                return jsonify({'error': 'Download failed - file not found'}), 500

            filename = os.path.basename(downloaded_filename)

            # Stream file to user
            def generate():
                with open(downloaded_filename, 'rb') as f:
                    while True:
                        chunk = f.read(8192)
                        if not chunk:
                            # Clean up after sending
                            try:
                                os.remove(downloaded_filename)
                            except:
                                pass
                            break
                        yield chunk

            response = Response(stream_with_context(generate()),
                              mimetype='application/octet-stream')
            response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            response.headers['Content-Length'] = os.path.getsize(downloaded_filename)

            return response

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Serve React app for all other routes (for production)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    """Serve React static files"""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    # Run cleanup on startup
    cleanup_old_files()

    print(f"Starting server...")
    print(f"Download folder: {DOWNLOAD_FOLDER}")
    print("Server running on http://localhost:5000")

    app.run(host='0.0.0.0', port=5000, debug=True)