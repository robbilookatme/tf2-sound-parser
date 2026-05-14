import requests, time, pathlib
from parser_types import *

url_base = "https://wiki.teamfortress.com/wiki/"
# Raw gives us the wiki markup version of the page rather than html
url_end = "?action=raw"

transcript_data_folder = "data/transcripts/"

def download_transcript(url):
    output_path = transcript_data_folder + url + ".txt"

    # Check if file already exists
    if pathlib.Path(output_path).is_file():
        return
    
    # sleep half a second between downloads to prevent spamming
    time.sleep(0.5)
    print("Downloading",url)
    res = requests.get(url_base + url + url_end)
    res.raise_for_status()
    
    text = res.text
    with open(output_path, "w") as f:
        f.write(res.text)

def download_transcripts():
    pathlib.Path(transcript_data_folder).mkdir(parents=True, exist_ok=True)
    for url in transcript_names:
        download_transcript(url)

if __name__ == "__main__":
    download_transcripts()
