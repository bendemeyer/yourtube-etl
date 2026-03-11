from typing import Generator
import requests
from urllib.parse import urlencode

from models.channel import Channel
from models.video import Video


base_url = "http://localhost:8080"

def add_channel(channel: Channel):
    print(f"Adding channel {channel.handle}: {channel.title}")
    result = requests.put(f"{base_url}/channel/{channel.id}", channel.to_json())
    if result.status_code != 200:
        raise Exception(result.json()["error"])

def add_video(video: Video):
    print(f"Adding video {video.id}: {video.title}")
    result = requests.put(f"{base_url}/video/{video.id}", video.to_json())
    if result.status_code != 200:
        raise Exception(result.json()["error"])

def get_latest_videos_by_channel(channel_id: str, batch_size: int = 20) -> list[Video]:
    result = requests.get(f"{base_url}/videos?channel={channel_id}&size={batch_size}")
    if result.status_code != 200:
        raise Exception(result.json()["error"])
    return [Video.from_dict(vid) for vid in result.json()["videos"]]

def get_channel(channel_id: str) -> Channel:
    result = requests.get(f"{base_url}/channel/{channel_id}")
    if result.status_code != 200:
        raise Exception(result.json()["error"])
    return Channel.from_dict(result.json()["channel"])

def get_channels(batch_size: int = 20) -> list[Channel]:
    result = requests.get(f"{base_url}/channels?size={batch_size}")
    if result.status_code != 200:
        raise Exception(result.json()["error"])
    return [Channel.from_dict(c) for c in result.json()["channels"]]

def generate_channels(params = None) -> Generator[Channel, None, None]:
    if params == None:
        params = {}
    if not "size" in params:
        params["size"] = 100
    complete = False
    next_page = None
    channels = []
    while not complete or len(channels) > 0:
        if channels:
            yield channels.pop(0)
        else:
            if next_page != None:
                params["pageToken"] = next_page
            result = requests.get(f"{base_url}/channels?{urlencode(params, doseq=True)}")
            if result.status_code != 200:
                raise Exception(result.json()["error"])
            content = result.json()
            if "nextPageToken" in content:
                next_page = content["nextPageToken"]
            else:
                complete = True
            channels.extend([Channel.from_dict(c) for c in content["channels"]])
