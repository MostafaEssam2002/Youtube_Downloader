
import requests
import re
import subprocess
import os
def constructor(url):
    pattern = r"(?:v=|\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    if match:
        video_id = match.group(1)
    else:
        return("No ID found.")
    url = "https://yt-api.p.rapidapi.com/dl"
    querystring = {"id": f"{video_id}", "cgeo": "DE"}
    headers = {
        "x-rapidapi-key": "4c229c9dfcmsh623acf1bbb20d36p1a10e0jsnc2f890a60eb2",
        "x-rapidapi-host": "yt-api.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring).json()
    return response

def get_strems(response):
    formats_dict = {}
    for format in response.get("adaptiveFormats", []):
        qualityLabel = format.get("qualityLabel")
        size = format.get("contentLength")
        if size:
            if int(size) > (1024 * 1024 * 1024):
                size = f"{round(int(size) / (1024 * 1024 * 1024), 2)} GB"
            elif int(size) > 1024 * 1024:
                size = f"{round(int(size) / (1024 * 1024), 2)} MB"
            elif int(size) > 1024:
                size = f"{round(int(size) / 1024, 2)} KB"
            format_info = {
                "size": size,
                "qualityLabel": qualityLabel if qualityLabel else "N/A",
                "url": format["url"]
            }
            if qualityLabel:
                formats_dict[qualityLabel] = format_info
            else:
                formats_dict["MP3"] = format_info
    return formats_dict

def get_download_link(url):
	formats=(constructor(url)["formats"][0])
	return (formats['url'])

def get_video_name(url):
	formats=constructor(url)
	return (formats['title'])

def get_video_length(url):
    try:
        formats = constructor(url)
        video_length = int(formats.get('lengthSeconds', 0))
        if video_length <= 0:
            return "Invalid or unknown video length."
        hours = video_length // 3600
        minutes = (video_length % 3600) // 60
        seconds = video_length % 60
        if hours > 0:
            return f"{hours:02}:{minutes:02}:{seconds:02}"  # hh:mm:ss
        elif minutes > 0:
            return f"{minutes:02}:{seconds:02}"  # mm:ss
        else:
            return f"{seconds:02}"  # ss
    except Exception as e:
        return f"An error occurred: {str(e)}"

def download_video(url, video_name="video"):
	response = requests.get(url, stream=True)
	if response.status_code == 200:
		with open(f"{video_name}.mp4", "wb") as f:
			for chunk in response.iter_content(chunk_size=1024):
				if chunk:
					f.write(chunk)
		print("File has been downloaded successfully.")
	else:
		print("Failed to download the video.")
def download_audio(url, video_name="video.mp3"):
	response = requests.get(url, stream=True)
	if response.status_code == 200:
		with open(f"{video_name}", "wb") as f:
			for chunk in response.iter_content(chunk_size=1024):
				if chunk:
					f.write(chunk)
		print("File has been downloaded successfully.")
	else:
		print("Failed to download the video.")


def merge_audio_video(audio_file, video_file, output_file):
    try:
        # Run the FFmpeg command to merge audio and video
        command = [
            "ffmpeg",
            "-i", video_file,
            "-i", audio_file,
            "-c:v", "copy",  # Copy the video codec without re-encoding
            "-c:a", "aac",   # Encode the audio to AAC (or use "copy" to avoid re-encoding)
            "-strict", "experimental",  # Ensure compatibility with older FFmpeg versions
            output_file
        ]
        subprocess.run(command, check=True)
        os.remove(video_file)
        os.remove(audio_file)
        print(f"Audio and video merged successfully into {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        return False

inp=input("Enter URL ")
print(""" choose number
    1- mp4
    2- mp3
    """)
typ=int(input())
if typ ==2:
    x=constructor(inp)
    print(get_strems(x)["MP3"]['size'])
    download_audio(get_strems(x)["MP3"]["url"])
else:
    x=constructor(inp)
    print(get_strems(x))
    resolution=input("Choose resolution ")
    print(get_strems(x)[resolution]['size'])
    download_video(get_strems(x)[f"{resolution}"]["url"])
    download_audio(get_strems(x)["MP3"]["url"])
    if merge_audio_video("video.mp3", "video.mp4", "output.mp4"):
        print("Merge completed!")
    else:
        print("Merge failed!")
