import requests
import re
class YouTubeVideo:
    def __init__(self, url):
        self.url = url
        self.api_host = "yt-api.p.rapidapi.com"
        self.api_url = "https://yt-api.p.rapidapi.com/dl"
        self.video_info = self._fetch_video_info()

    def _extract_video_id(self):
        pattern = r"(?:v=|\/)([a-zA-Z0-9_-]{11})"
        match = re.search(pattern, self.url)
        if match:
            return match.group(1)
        else:
            raise ValueError("Invalid YouTube URL. No video ID found.")

    def _fetch_video_info(self):
        try:
            video_id = self._extract_video_id()
            querystring = {"id": video_id, "cgeo": "DE"}
            headers = {
                "x-rapidapi-key": "4c229c9dfcmsh623acf1bbb20d36p1a10e0jsnc2f890a60eb2",
                "x-rapidapi-host": self.api_host,
            }
            response = requests.get(self.api_url, headers=headers, params=querystring)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to fetch video info. Status code: {response.status_code}")
        except Exception as e:
            raise Exception(f"An error occurred while fetching video info: {str(e)}")

    @property
    def video_name(self):
        return self.video_info.get("title", "Unknown Title")

    @property
    def video_length(self):
        try:
            video_length = int(self.video_info.get("lengthSeconds", 0))
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
            return f"An error occurred while calculating video length: {str(e)}"

    def get_download_link(self):
        if "formats" in self.video_info:
            return self.video_info["formats"][0]["url"]
        else:
            return "Download link not available."

    def download_video(self, video_name="video.mp4"):
        try:
            download_url = self.get_download_link()
            if not download_url.startswith("http"):
                raise Exception("Failed to get a valid download link.")
            response = requests.get(download_url, stream=True)
            if response.status_code == 200:
                with open(f"{video_name}.mp4", "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                print("File has been downloaded successfully.")
            else:
                raise Exception("Failed to download the video.")
        except Exception as e:
            print(f"An error occurred while downloading the video: {str(e)}")
