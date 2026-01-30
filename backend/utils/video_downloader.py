import yt_dlp
import os

def download_video(url, output_path):
    """
    Downloads a video from a URL (YouTube, etc.) using yt-dlp.
    Includes headers to bypass bot detection.
    """
    ydl_opts = {
        # Select best mp4 format available
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_path,
        'quiet': False,
        'no_warnings': False,
        # Mimic a real browser to avoid being blocked
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        },
    }

    try:
        # If output file already exists (from a failed run), remove it
        if os.path.exists(output_path):
            os.remove(output_path)

        print(f"🚀 [yt-dlp] Attempting to download: {url}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            error_code = ydl.download([url])
            if error_code != 0:
                return False, f"yt-dlp returned error code {error_code}"
        
        # Verify file exists and has content
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            if size > 0:
                print(f"✅ Download complete! Size: {size} bytes")
                return True, None
            else:
                return False, "The downloaded file is 0 bytes (empty)."
        
        return False, "File was not saved to disk."

    except Exception as e:
        return False, str(e)