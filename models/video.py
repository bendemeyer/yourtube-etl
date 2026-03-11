import json

from typing import Self

class Video:
    def __init__(self, id: str, channel_id: str, title: str, description: str, duration: int, thumbnails: list[str], is_short: bool, published: str):
        self.id: str = id
        self.channel_id: str = channel_id
        self.title: str = title
        self.description: str = description
        self.duration: int = duration
        self.thumbnails: list[str] = thumbnails
        self.is_short: bool = is_short
        self.published: str = published

    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "channelId": self.channel_id,
            "title": self.title,
            "description": self.description,
            "duration": self.duration,
            "thumbnails": self.thumbnails,
            "isShort": self.is_short,
            "published": self.published,
        })

    @classmethod
    def from_dict(cls, data) -> Self:
        return cls(
            data["id"],
            data["channel"]["id"],
            data["title"],
            data.get("description", ""),
            data["duration"],
            data["thumbnails"],
            data.get("isShort", False),
            data["published"],
        )
