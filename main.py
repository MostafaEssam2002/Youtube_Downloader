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
        self.url = url  # حفظ URL في الخاصية
        return response

    @property
    def get_video_name(self):
        if not self.video_data:
            raise ValueError("Video data has not been fetched yet.")
        return self.video_data.get("title", "Unknown Title")

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

    def download_file(self, url, filename, save_path):
        full_path = os.path.join(save_path, filename)
        max_retries = 5
        retry_count = 0
        downloaded = False
        while not downloaded and retry_count < max_retries:
            try:
                response = requests.get(url, stream=True, timeout=10)
                response.raise_for_status()  # Raise HTTP errors if they occur
                total_size = int(response.headers.get('content-length', 0))  # إجمالي حجم الملف إذا كان موجودًا
                downloaded_size = 0  # لتتبع الحجم الذي تم تنزيله
                with open(full_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)  # إضافة حجم الشريحة إلى الحجم الذي تم تنزيله
                            # طباعة تقدم التنزيل
                            print(f"Downloaded: {self.format_size(downloaded_size)} of {self.format_size(total_size)}", end="\r")
                downloaded = True
                print(f"\nFile {filename} downloaded successfully to {save_path}.")
            except requests.exceptions.ChunkedEncodingError as e:
                retry_count += 1
                print(f"ChunkedEncodingError occurred: {e}. Retrying {retry_count}/{max_retries}...")
                time.sleep(2)  # Wait before retrying
            except requests.exceptions.RequestException as e:
                print(f"Download failed: {e}")
                break
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                break

        if not downloaded:
            print(f"Failed to download {filename} after {max_retries} attempts.")



    def merge_audio_video(self, audio_file, video_file, output_file=get_video_name, save_path=os.getcwd()):
        # def converter(input_video, input_audio, output_video):
        ffmpeg_command = r'ffmpeg.exe -i "{input}" -an -vcodec copy "{output}"'.format(input=video_file, output=output_file)
        ffmpeg_command = (fr'ffmpeg.exe -i "{video_file}" -i "{audio_file}" -c:v copy -c:a aac -strict experimental "{output_file}"')
        process = subprocess.Popen(shlex.split(ffmpeg_command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate()  
        if process.returncode == 0:
            print("Audio added to the video successfully.")
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

save_path = input("Enter the directory to save the file (leave blank for current directory): ")
# if not save_path:
#     save_path = os.getcwd()  # المسار الحالي

print("""Choose number:
1- MP4
2- MP3
""")
choice = int(input("Enter your choice: "))
print("*"*50)
print(downloader.get_video_name)
print("*"*50)
streams = downloader.get_streams()

if choice == 2:
    mp3_stream = streams.get("MP3")
    if mp3_stream:
        print(f"Audio size: {mp3_stream['size']}")
        downloader.download_file(mp3_stream["url"], "audio.mp3", save_path)
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
        downloader.download_file(video_stream["url"], "video.mp4", save_path)

        mp3_stream = streams.get("MP3")
        if mp3_stream:
            downloader.download_file(mp3_stream["url"], "audio.mp3", save_path)
            downloader.merge_audio_video(
                os.path.join(save_path, "audio.mp3"),
                os.path.join(save_path, "video.mp4"),
                "output.mp4",
                save_path
            )
        else:
            print("No MP3 stream found.")
    else:
        print("Resolution not found.")

