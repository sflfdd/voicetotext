import os
import requests
from tqdm import tqdm

def download_file(url, filename):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    os.makedirs('models', exist_ok=True)
    
    with open(os.path.join('models', filename), 'wb') as file, tqdm(
        desc=filename,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            pbar.update(size)

def main():
    # URLs for Arabic DeepSpeech model files
    model_url = "https://github.com/AASHISHAG/deepspeech-arabic/releases/download/v0.9.3/arabic.pbmm"
    scorer_url = "https://github.com/AASHISHAG/deepspeech-arabic/releases/download/v0.9.3/arabic.scorer"
    
    print("Downloading Arabic DeepSpeech model files...")
    download_file(model_url, "arabic.pbmm")
    download_file(scorer_url, "arabic.scorer")
    print("Download complete!")

if __name__ == "__main__":
    main()
