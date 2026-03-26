import React from 'react';

export default function VideoInfo({ videoInfo, onFormatSelect, audioOnly, onAudioToggle }) {
  if (!videoInfo) return null;

  const formatMinutes = (duration) => {
    if (!duration) return 'N/A';
    const minutes = Math.floor(duration / 60);
    const seconds = duration % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className="video-info">
      <div className="video-preview">
        {videoInfo.thumbnail ? (
          <img src={videoInfo.thumbnail} alt={videoInfo.title} className="thumbnail" />
        ) : (
          <div className="thumbnail" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#999' }}>
            No thumbnail
          </div>
        )}
        <div className="video-details">
          <h3>{videoInfo.title}</h3>
          <p className="meta-info">
            <strong>Duration:</strong> {videoInfo.duration_str || formatMinutes(videoInfo.duration)}
          </p>
          {videoInfo.uploader && (
            <p className="meta-info">
              <strong>Uploader:</strong> {videoInfo.uploader}
            </p>
          )}
          {videoInfo.platform && (
            <p className="meta-info">
              <strong>Platform:</strong> {videoInfo.platform}
            </p>
          )}
        </div>
      </div>

      {videoInfo.formats && videoInfo.formats.length > 0 && (
        <div className="quality-section">
          <div className="audio-toggle">
            <input
              type="checkbox"
              id="audio-only"
              checked={audioOnly}
              onChange={onAudioToggle}
            />
            <label htmlFor="audio-only">
              <strong>Audio Only</strong> (download as MP3)
            </label>
          </div>

          <label htmlFor="quality-select">Select Quality:</label>
          <select
            id="quality-select"
            className="quality-select"
            onChange={(e) => onFormatSelect(e.target.value)}
            defaultValue=""
            disabled={audioOnly}
          >
            <option value="" disabled>
              Choose quality...
            </option>
            {videoInfo.formats
              .filter(fmt => audioOnly ? (fmt.quality.toLowerCase().includes('audio') || fmt.type === 'audio') : !(fmt.quality.toLowerCase().includes('audio') || fmt.type === 'audio'))
              .map((format, index) => (
                <option key={index} value={format.format_id}>
                  {format.quality}
                  {format.filesize_mb && ` (${format.filesize_mb} MB)`}
                  {format.ext && ` - ${format.ext.toUpperCase()}`}
                </option>
              ))
            }
          </select>
        </div>
      )}
    </div>
  );
}