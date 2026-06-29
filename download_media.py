import os
import urllib.request
import shutil

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(BASE_DIR, "media")
AUDIO_DIR = os.path.join(MEDIA_DIR, "audio")
VIDEO_DIR = os.path.join(MEDIA_DIR, "video")
IMAGES_DIR = os.path.join(MEDIA_DIR, "images")

# Create folders
for folder in [AUDIO_DIR, VIDEO_DIR, IMAGES_DIR]:
    os.makedirs(folder, exist_ok=True)

# Sample media URLs
AUDIO_URL = "https://raw.githubusercontent.com/rafaelreis-hotmart/Audio-Sample-files/master/sample.mp3"
VIDEO_URL = "https://github.com/mediaelement/mediaelement-files/blob/master/big_buck_bunny.mp4?raw=true"

# Target slugs
SLUGS = [
    "urinary-catheterisation",
    "cardiopulmonary-resuscitation",
    "intravenous-cannulation",
    "sterile-wound-dressing"
]

def download_file(url, dest_path):
    print(f"Downloading {url} -> {dest_path}...")
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(dest_path, "wb") as f:
                f.write(response.read())
        print(f"Downloaded successfully: {os.path.basename(dest_path)}")
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

def main():
    temp_audio = os.path.join(MEDIA_DIR, "temp_sample.mp3")
    temp_video = os.path.join(MEDIA_DIR, "temp_sample.mp4")
    
    # Download source audio and video
    audio_ok = download_file(AUDIO_URL, temp_audio)
    video_ok = download_file(VIDEO_URL, temp_video)
    
    # If audio download failed, write a mock audio file
    if not audio_ok:
        print("Creating mock blank audio file...")
        with open(temp_audio, "wb") as f:
            f.write(b"ID3\x03\x00\x00\x00\x00\x00\x00" + b"\x00" * 1000) # Mock header
            
    # If video download failed, write a mock video file
    if not video_ok:
        print("Creating mock blank video file...")
        with open(temp_video, "wb") as f:
            f.write(b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 1000) # Mock header

    # Replicate for each slug
    for slug in SLUGS:
        shutil.copy2(temp_audio, os.path.join(AUDIO_DIR, f"{slug}.mp3"))
        shutil.copy2(temp_video, os.path.join(VIDEO_DIR, f"{slug}.mp4"))
        print(f"Copied media files for {slug}")
        
    # Cleanup temp files
    if os.path.exists(temp_audio):
        os.remove(temp_audio)
    if os.path.exists(temp_video):
        os.remove(temp_video)
        
    print("Media asset setup complete.")

if __name__ == "__main__":
    main()
