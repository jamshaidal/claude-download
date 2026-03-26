import React from 'react';

export default function UrlInput({ url, onUrlChange, onFetch, loading }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    onFetch();
  };

  return (
    <form onSubmit={handleSubmit} className="input-group">
      <label htmlFor="video-url">Video URL</label>
      <input
        id="video-url"
        type="text"
        className="url-input"
        placeholder="Paste video URL from YouTube, Facebook, TikTok, Instagram..."
        value={url}
        onChange={(e) => onUrlChange(e.target.value)}
        disabled={loading}
      />
    </form>
  );
}