import argparse
from datetime import datetime, timezone

import yourtube_api
import yt

from models.channel import Channel


def init_channel_by_url(channel_url: str):
    handle = next(part for part in channel_url.split("/") if part.startswith("@"))
    init_channel_by_handle(handle)


def init_channel_by_handle(channel_name: str, users: list[int]):
    channel_id = yt.get_channel_id_from_handle(channel_name)
    channel = yt.get_channel(channel_id)
    yourtube_api.add_channel(channel)
    for user in users:
        yourtube_api.add_user_channel(user, channel)
    yourtube_api.add_user_channel(channel, )
    for batch in yt.generate_video_batches_by_channel(channel):
        for video in batch:
            yourtube_api.add_video(video)


def update_channel(channel: Channel):
    latest_vid = yourtube_api.get_latest_videos_by_channel(channel.id, 1)
    timestamp = datetime.fromtimestamp(0).replace(tzinfo=timezone.utc)
    if len(latest_vid) > 0:
        timestamp = datetime.fromisoformat(latest_vid[0].published.replace('Z', '+00:00'))
    for batch in yt.generate_video_batches_by_channel(channel, timestamp):
        for video in batch:
            yourtube_api.add_video(video)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("YourTube Data Updater")
    parser.add_argument("host", help="The YourTube API host")
    parser.add_argument("--update", dest="update", nargs="*", help="Update existing channels. Specify one or more channels to update them. If no channels are explicitly specified, all channels will be updated.")
    parser.add_argument("--add", dest="add", nargs="+", help="Add new channels to the database. Specify one or more channels to add them.")
    parser.add_argument("--users", type=int, dest="user", nargs="+", help="User IDs to associate with any newly added channels")

    args = parser.parse_args()

    yourtube_api.base_url = args.host

    if args.update != None:
        if len(args.update) == 0:
            channels = yourtube_api.generate_channels()
        else:
            channels = yourtube_api.generate_channels({"handle": [args.update]})
        for channel in channels:
            update_channel(channel)

    if args.add:
        users = args.users or []
        for handle in args.add:
            init_channel_by_handle(handle, users)
