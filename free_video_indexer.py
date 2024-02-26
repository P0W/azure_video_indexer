import json
import time
import uuid
import requests


class AzureVideoIndexer:
    """Class to interact"""

    def __init__(self, config_file):
        self.config_file = config_file
        self.AccountId = None
        self.location = None
        self.API_KEY = None
        self.accessToken = None
        self.get_details()

    def get_details(self):
        """Gets the access token for Video Indexer."""
        with open(self.config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
            self.AccountId = config["AccountId"]
            self.location = config["location"]
            self.API_KEY = config["API_KEY"]

            headers = {
                "Ocp-Apim-Subscription-Key": self.API_KEY,
                "x-ms-client-request-id": str(uuid.uuid4()),
            }
            response = requests.get(
                f"https://api.videoindexer.ai/Auth/{self.location}/Accounts/{self.AccountId}/AccessToken?allowEdit=true",
                headers=headers,
            )
            response.raise_for_status()
            self.accessToken = response.json()

    def upload_for_indexing(self, media_path, name, description):
        """Uploads a video to Video Indexer for indexing and analysis. Returns the video ID."""
        privacy = "Private"
        partition = "demos"

        url = f"https://api.videoindexer.ai/{self.location}/Accounts/{self.AccountId}/Videos"
        params = {
            "name": name,
            "description": description,
            "privacy": privacy,
            "partition": partition,
            "accessToken": self.accessToken,
        }

        response = requests.post(
            url, params=params, files={"file": open(media_path, "rb")}
        )
        response.raise_for_status()
        video_id = response.json()
        id = video_id.get("id")
        print("Videod id", id)
        return id

    def get_indexed_video(self, video_id):
        """Gets the indexed video from Video Indexer."""
        response = requests.get(
            f"https://api.videoindexer.ai/{self.location}/Accounts/{self.AccountId}/Videos/{video_id}/Index?accessToken={self.accessToken}"
        )
        # print(response)
        response.raise_for_status()
        video = response.json()
        return video

    def wait_for_indexing(self, video_id):
        """Waits for the video to be processed and indexed. Returns the indexed video."""
        processing = False
        while not processing:
            print("Waiting for video to be processed...")
            video = self.get_indexed_video(video_id)
            processing = video.get("state") == "Processed"
            time.sleep(5)
        return video


if __name__ == "__main__":
    videoIndexer = AzureVideoIndexer("config.json")
    video_id = videoIndexer.upload_for_indexing(
        media_path=r"D:\Projects\media\1TRILLIONmessages.mp4",
        name="1TRILLIONmessages",
        description="1 Trilion Messages",
    )
    video_json = videoIndexer.wait_for_indexing(video_id)
    with open(f"response_video_{video_id}.json", "w") as f:
        json.dump(video_json, f, indent=2)
