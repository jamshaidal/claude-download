#!/usr/bin/env python3
"""
Manual test script for the video downloader backend.
Run: python test_backend.py
"""

import requests
import json
import sys

BACKEND_URL = "http://localhost:5000"

def test_health():
    print("\n=== Testing Health Check ===")
    try:
        response = requests.get(f"{BACKEND_URL}/api/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_get_info(url):
    print(f"\n=== Testing Get Info ===")
    print(f"URL: {url}")
    try:
        response = requests.post(f"{BACKEND_URL}/api/info", json={"url": url})
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Title: {data.get('title')}")
            print(f"Platform: {data.get('platform')}")
            print(f"Duration: {data.get('duration_str')}")
            print(f"Thumbnail: {data.get('thumbnail', 'None')[:50]}...")
            print(f"Number of formats: {len(data.get('formats', []))}")
            for i, fmt in enumerate(data.get('formats', [])[:5]):  # Show first 5
                print(f"  {i+1}. {fmt['quality']} - {fmt['ext']} - {fmt.get('filesize_mb', 'N/A')} MB")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("Video Downloader Backend Test")
    print("=" * 50)

    # Test health first
    if not test_health():
        print("\nHealth check failed. Is the backend running?")
        print("Start with: cd backend && python app.py")
        sys.exit(1)

    # Test with sample URLs
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Astley
    ]

    for url in test_urls:
        test_get_info(url)

    print("\n" + "=" * 50)
    print("Tests complete!")
    print("\nTo test download manually, visit:")
    print(f"  Frontend: http://localhost:3000")
    print(f"  Backend:  {BACKEND_URL}")
    print("\nOr use curl to test download:")
    print(f"  curl -OJ '{BACKEND_URL}/api/download/123?url={test_urls[0]}&format_id=best'")

if __name__ == "__main__":
    try:
        import requests
        main()
    except ImportError:
        print("Error: requests library not found.")
        print("Install it: pip install requests")
        sys.exit(1)