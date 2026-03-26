const API_BASE = '/api';

export async function getVideoInfo(url) {
  const response = await fetch(`${API_BASE}/info`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to fetch video info');
  }

  return response.json();
}

export async function downloadVideo(url, formatId, audioOnly = false) {
  const params = new URLSearchParams({
    url,
    format_id: formatId,
    audio_only: audioOnly.toString(),
  });

  window.location.href = `${API_BASE}/download/${Date.now()}?${params.toString()}`;
}