import React, { useState } from 'react';
import UrlInput from './components/UrlInput';
import VideoInfo from './components/VideoInfo';
import ErrorMessage from './components/ErrorMessage';
import { getVideoInfo, downloadVideo } from './api';

function App() {
  const [url, setUrl] = useState('');
  const [videoInfo, setVideoInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedFormat, setSelectedFormat] = useState('');
  const [audioOnly, setAudioOnly] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const handleFetch = async () => {
    if (!url.trim()) {
      setError('Please enter a URL');
      return;
    }

    setLoading(true);
    setError('');
    setVideoInfo(null);
    setSelectedFormat('');

    try {
      const info = await getVideoInfo(url);
      setVideoInfo(info);
      // Auto-select first format
      if (info.formats && info.formats.length > 0) {
        const firstVideoFormat = info.formats.find(f => !f.quality.toLowerCase().includes('audio') && f.type !== 'audio');
        if (firstVideoFormat) {
          setSelectedFormat(firstVideoFormat.format_id);
        }
      }
    } catch (err) {
      setError(err.message || 'Failed to fetch video information');
    } finally {
      setLoading(false);
    }
  };

  const handleFormatSelect = (formatId) => {
    setSelectedFormat(formatId);
  };

  const handleAudioToggle = (e) => {
    const checked = e.target.checked;
    setAudioOnly(checked);
    setSelectedFormat('');
  };

  const handleDownload = async () => {
    if (!url.trim()) {
      setError('Please enter a URL first');
      return;
    }

    if (!selectedFormat && !audioOnly) {
      setError('Please select a quality');
      return;
    }

    setDownloading(true);
    setError('');

    try {
      if (audioOnly) {
        await downloadVideo(url, 'bestaudio', true);
      } else {
        await downloadVideo(url, selectedFormat, false);
      }
    } catch (err) {
      setError(err.message || 'Download failed');
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="container">
      <h1>Video Downloader</h1>

      <div className="disclaimer">
        <strong>Disclaimer:</strong> Only download videos you have permission to download.
        Respect copyright and platform terms of service.
      </div>

      <UrlInput url={url} onUrlChange={setUrl} onFetch={handleFetch} loading={loading} />

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Fetching video information...</p>
        </div>
      )}

      {error && <ErrorMessage message={error} />}

      {!loading && videoInfo && (
        <VideoInfo
          videoInfo={videoInfo}
          onFormatSelect={handleFormatSelect}
          audioOnly={audioOnly}
          onAudioToggle={handleAudioToggle}
        />
      )}

      {!loading && videoInfo && (
        <button
          className="button download-button"
          onClick={handleDownload}
          disabled={downloading || (!selectedFormat && !audioOnly)}
        >
          {downloading ? 'Downloading...' : `Download ${audioOnly ? 'Audio' : 'Video'}`}
        </button>
      )}
    </div>
  );
}

export default App;