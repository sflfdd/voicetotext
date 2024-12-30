import os
import sys
import urllib.request
import zipfile
import shutil

def download_ffmpeg():
    print("Downloading FFmpeg...")
    url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    zip_path = "ffmpeg.zip"
    
    # Download the zip file
    urllib.request.urlretrieve(url, zip_path)
    
    # Extract the zip file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall("temp_ffmpeg")
    
    # Move the ffmpeg.exe to the current directory
    ffmpeg_dir = os.path.join("temp_ffmpeg", "ffmpeg-master-latest-win64-gpl", "bin")
    for file in os.listdir(ffmpeg_dir):
        if file.endswith('.exe'):
            shutil.copy2(os.path.join(ffmpeg_dir, file), ".")
    
    # Clean up
    os.remove(zip_path)
    shutil.rmtree("temp_ffmpeg")
    print("FFmpeg setup complete!")

if __name__ == "__main__":
    if not os.path.exists("ffmpeg.exe"):
        download_ffmpeg()
    else:
        print("FFmpeg already exists!")
