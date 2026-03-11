import requests
import isodate


from datetime import datetime, timezone
from urllib.parse import urlencode
from typing import Generator

from models.channel import Channel
from models.video import Video
from settings import API_KEY


def _build_api_request_url(endpoint, kwargs) -> str:
    url = f"https://www.googleapis.com/youtube/v3/{endpoint}?key={API_KEY}"
    return "&".join([url, urlencode(kwargs)])


def generate_video_batches_by_channel(channel: Channel, last_check: datetime = datetime.fromtimestamp(0).replace(tzinfo=timezone.utc), batch_size: int = 50) -> Generator[list[Video], None, None]:
    next_page_token = None
    short_ids = generate_short_ids_by_channel(channel)
    latest_short_id = next(short_ids)
    complete = False
    buffer = []
    while complete == False or len(buffer) > 0:
        while len(buffer) < batch_size and complete == False:
            initialParams = {
                "playlistId": channel.uploads_playlist(),
                "part": "snippet",
                "max_results": 50
            }
            if next_page_token is not None:
                initialParams["pageToken"] = next_page_token
            url = _build_api_request_url("playlistItems", initialParams)
            initialResults = requests.get(url).json()
            if "nextPageToken" not in initialResults:
                complete = True
            else:
                next_page_token = initialResults["nextPageToken"]

            vidIds = [item["snippet"]["resourceId"]["videoId"] for item in initialResults["items"] 
                      if datetime.fromisoformat(item["snippet"]["publishedAt"]) > last_check]
            if len(vidIds) < len(initialResults["items"]):
                complete = True

            detailParams = {
                "id": ",".join(vidIds),
                "part": "snippet,contentDetails",
            }
            url = _build_api_request_url("videos", detailParams)
            detailResults = requests.get(url).json()
            for item in detailResults["items"]:
                if item["kind"] != "youtube#video":
                    continue
                is_short = False
                if item["id"] == latest_short_id:
                    is_short = True
                    try:
                        latest_short_id = next(short_ids)
                    except StopIteration:
                        latest_short_id = None
                buffer.append(Video(
                    item["id"],
                    item["snippet"]["channelId"],
                    item["snippet"]["title"],
                    item["snippet"]["description"],
                    int(isodate.parse_duration(item["contentDetails"]["duration"]).total_seconds()),
                    [v["url"] for k, v in item["snippet"]["thumbnails"].items()],
                    is_short,
                    item["snippet"]["publishedAt"],
                ))
        batch = buffer[:batch_size]
        buffer = buffer[batch_size:]
        yield batch


def generate_short_ids_by_channel(channel: Channel) -> Generator[str, None, None]:
    next_page_token = None
    complete = False
    buffer = []
    while complete == False or len(buffer) > 0:
        if len(buffer) < 1:
            params = {
                "playlistId": channel.shorts_playlist(),
                "part": "snippet",
                "max_results": 50
            }
            if next_page_token is not None:
                params["pageToken"] = next_page_token
            url = _build_api_request_url("playlistItems", params)
            results = requests.get(url).json()
            if "nextPageToken" not in results:
                complete = True
            else:
                next_page_token = results["nextPageToken"]
            buffer.extend([item["snippet"]["resourceId"]["videoId"] for item in results["items"]])
        yield buffer.pop(0)


def get_channel(channel_id) -> Channel:
    url = _build_api_request_url("channels", {
        "part": "snippet",
        "id": channel_id
    })
    result = requests.get(url).json().get("items")[0]
    return Channel(
        result["id"],
        result["snippet"]["customUrl"],
        result["snippet"]["title"],
        result["snippet"]["description"],
        [v["url"] for k, v in result["snippet"]["thumbnails"].items()]
    )


def get_channel_id_from_handle(handle: str) -> str:
    url = _build_api_request_url("channels", {
        "part": "id",
        "forHandle": handle
    })
    return requests.get(url).json().get("items")[0]["id"]