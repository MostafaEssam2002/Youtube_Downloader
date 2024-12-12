import shlex
import requests
import re
import subprocess
import os
import time

class YouTubeDownloader:
    def __init__(self, api_key, api_host):
        self.api_key = api_key
        self.api_host = api_host
        self.video_data = {}

    def extract_video_id(self, url):
        pattern = r"(?:v=|\/)([a-zA-Z0-9_-]{11})"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None

    def fetch_video_data(self, url):
        video_id = self.extract_video_id(url)
        if not video_id:
            raise ValueError("No video ID found in the URL.")

        api_url = "https://yt-api.p.rapidapi.com/dl"
        querystring = {"id": video_id, "cgeo": "DE"}
        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.api_host
        }
        response = requests.get(api_url, headers=headers, params=querystring).json()
        self.video_data = response
        self.url = url
        return response

    @property
    def get_video_name(self):
        if not self.video_data:
            raise ValueError("Video data has not been fetched yet.")
        # Replace invalid characters with an underscore
        title = self.video_data.get("title", "Unknown_Title")
        invalid_chars = r'[<>:"/\\|?*]'
        return re.sub(invalid_chars, "_", title.replace(" ", "_"))

    def get_streams(self):
        formats_dict = {}
        for format in self.video_data.get("adaptiveFormats", []):
            quality_label = format.get("qualityLabel")
            size = format.get("contentLength")
            if size:
                size = self.format_size(int(size))
                format_info = {
                    "size": size,
                    "qualityLabel": quality_label if quality_label else "N/A",
                    "url": format["url"]
                }
                formats_dict[quality_label or "MP3"] = format_info
        return formats_dict

    @staticmethod
    def format_size(size):
        if size > (1024 * 1024 * 1024):
            return f"{round(size / (1024 * 1024 * 1024), 2)} GB"
        elif size > 1024 * 1024:
            return f"{round(size / (1024 * 1024), 2)} MB"
        elif size > 1024:
            return f"{round(size / 1024, 2)} KB"
        return f"{size} Bytes"

    def download_file(self, url, save_path, filename):
        full_path = os.path.join(save_path, filename)
        max_retries = 5
        retry_count = 0
        downloaded = False
        while not downloaded and retry_count < max_retries:
            try:
                response = requests.get(url, stream=True, timeout=10)
                response.raise_for_status()
                total_size = int(response.headers.get('content-length', 0))
                downloaded_size = 0
                with open(full_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            print(f"Downloaded: {self.format_size(downloaded_size)} of {self.format_size(total_size)}", end="\r")
                downloaded = True
                print(f"\nFile {filename} downloaded successfully to {save_path}.")
            except requests.exceptions.ChunkedEncodingError as e:
                retry_count += 1
                print(f"ChunkedEncodingError occurred: {e}. Retrying {retry_count}/{max_retries}...")
                time.sleep(2)
            except requests.exceptions.RequestException as e:
                print(f"Download failed: {e}")
                break
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                break
        if not downloaded:
            print(f"Failed to download {filename} after {max_retries} attempts.")

    def merge_audio_video(self, audio_file, video_file, save_path):
        video_name = os.path.splitext(os.path.basename(video_file))[0]
        output_file = os.path.join(save_path, f"{video_name}_merged.mp4")
        ffmpeg_command = (
            fr'ffmpeg -i "{video_file}" -i "{audio_file}" '
            fr'-c:v copy -c:a aac -strict experimental "{output_file}"'
        )
        process = subprocess.Popen(shlex.split(ffmpeg_command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate()
        if process.returncode == 0:
            print(f"Audio added to the video successfully. Output saved to: {output_file}")
        else:
            print("An error occurred while adding audio to the video.")
        os.remove(audio_file)
        os.remove(video_file)

downloader = YouTubeDownloader(
    api_key="4c229c9dfcmsh623acf1bbb20d36p1a10e0jsnc2f890a60eb2",
    api_host="yt-api.p.rapidapi.com"
)

url = input("Enter YouTube URL: ")
downloader.fetch_video_data(url)
save_path = input("Enter the directory to save the file (leave blank for current directory): ") or "."

print("""Choose number:
1- MP4
2- MP3
""")
choice = int(input("Enter your choice: "))
print("*" * 50)
print(downloader.get_video_name)
print("*" * 50)

streams = downloader.get_streams()
if choice == 2:
    mp3_stream = streams.get("MP3")
    if mp3_stream:
        print(f"Audio size: {mp3_stream['size']}")
        downloader.download_file(mp3_stream["url"], save_path, f"{downloader.get_video_name}.mp3")
    else:
        print("No MP3 stream found.")
else:
    print("Available resolutions:")
    for quality, info in streams.items():
        print(f"{quality}: {info['size']}")
    resolution = input("Choose resolution: ")
    video_stream = streams.get(resolution)
    if video_stream:
        print(f"Video size: {video_stream['size']}")
        downloader.download_file(video_stream["url"], save_path, f"{downloader.get_video_name}.mp4")
        mp3_stream = streams.get("MP3")
        if mp3_stream:
            downloader.download_file(mp3_stream["url"], save_path, f"{downloader.get_video_name}_audio.mp3")
            downloader.merge_audio_video(
                os.path.join(save_path, f"{downloader.get_video_name}_audio.mp3"),
                os.path.join(save_path, f"{downloader.get_video_name}.mp4"),
                save_path
            )
        else:
            print("No MP3 stream found.")
    else:
        print("Resolution not found.")

input("Enter any key to exit ")
