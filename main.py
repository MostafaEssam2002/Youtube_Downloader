
import requests
import re
def constructor(url):
    # استخراج معرّف الفيديو من الرابط
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
            # تحويل الحجم إلى صيغة قابلة للقراءة
            if int(size) > (1024 * 1024 * 1024):
                size = f"{round(int(size) / (1024 * 1024 * 1024), 2)} GB"
            elif int(size) > 1024 * 1024:
                size = f"{round(int(size) / (1024 * 1024), 2)} MB"
            elif int(size) > 1024:
                size = f"{round(int(size) / 1024, 2)} KB"
            # تخزين المعلومات في القاموس
            format_info = {
                "size": size,
                "qualityLabel": qualityLabel if qualityLabel else "N/A",
                "url": format["url"]
            }
            # إضافة البيانات إلى القاموس باستخدام qualityLabel كـ مفتاح
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

def download_video(url, video_name="video.mp4"):
	format = constructor(url)["formats"][0]
	download_url = format['url']
	response = requests.get(download_url, stream=True)
	if response.status_code == 200:
		with open(f"{video_name}.mp4", "wb") as f:
			for chunk in response.iter_content(chunk_size=1024):
				if chunk:
					f.write(chunk)
		print("File has been downloaded successfully.")
	else:
		print("Failed to download the video.")
x=constructor("https://www.youtube.com/watch?v=4WknYA9zcNY")
# print(get_strems(x)["720p"])
print(get_strems(x))
# print(x)

# class YouTubeVideo:
#     def __init__(self, url):
#         self.url = url
#         self.api_host = "yt-api.p.rapidapi.com"
#         self.api_url = "https://yt-api.p.rapidapi.com/dl"
#         self.video_info = self._fetch_video_info()

#     def _extract_video_id(self):
#         pattern = r"(?:v=|\/)([a-zA-Z0-9_-]{11})"
#         match = re.search(pattern, self.url)
#         if match:
#             return match.group(1)
#         else:
#             raise ValueError("Invalid YouTube URL. No video ID found.")

#     def _fetch_video_info(self):
#         try:
#             video_id = self._extract_video_id()
#             querystring = {"id": video_id, "cgeo": "DE"}
#             headers = {
#                 "x-rapidapi-key": "4c229c9dfcmsh623acf1bbb20d36p1a10e0jsnc2f890a60eb2",
#                 "x-rapidapi-host": self.api_host,
#             }
#             response = requests.get(self.api_url, headers=headers, params=querystring)
#             if response.status_code == 200:
#                 return response.json()
#             else:
#                 raise Exception(f"Failed to fetch video info. Status code: {response.status_code}")
#         except Exception as e:
#             raise Exception(f"An error occurred while fetching video info: {str(e)}")

#     @property
#     def video_name(self):
#         return self.video_info.get("title", "Unknown Title")

#     @property
#     def video_length(self):
#         try:
#             video_length = int(self.video_info.get("lengthSeconds", 0))
#             if video_length <= 0:
#                 return "Invalid or unknown video length."
#             hours = video_length // 3600
#             minutes = (video_length % 3600) // 60
#             seconds = video_length % 60
#             if hours > 0:
#                 return f"{hours:02}:{minutes:02}:{seconds:02}"  # hh:mm:ss
#             elif minutes > 0:
#                 return f"{minutes:02}:{seconds:02}"  # mm:ss
#             else:
#                 return f"{seconds:02}"  # ss
#         except Exception as e:
#             return f"An error occurred while calculating video length: {str(e)}"

#     def get_download_link(self):
#         if "formats" in self.video_info:
#             return self.video_info["formats"][0]["url"]
#         else:
#             return "Download link not available."

#     def download_video(self, video_name="video.mp4"):
#         try:
#             download_url = self.get_download_link()
#             if not download_url.startswith("http"):
#                 raise Exception("Failed to get a valid download link.")
#             response = requests.get(download_url, stream=True)
#             if response.status_code == 200:
#                 with open(f"{video_name}.mp4", "wb") as f:
#                     for chunk in response.iter_content(chunk_size=1024):
#                         if chunk:
#                             f.write(chunk)
#                 print("File has been downloaded successfully.")
#             else:
#                 raise Exception("Failed to download the video.")
#         except Exception as e:
#             print(f"An error occurred while downloading the video: {str(e)}")


# # Example Usage:0
# video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
# # Create an instance of YouTubeVideo
# video = YouTubeVideo(video_url)
# # Get video details
# print("Video Title:", video.video_name)
# print("Video Length:", video.video_length)
# # Download the video
# video.download_video("my_video")
