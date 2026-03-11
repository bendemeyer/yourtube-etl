import json

from typing import Self

class Channel:
    def __init__(self, id: str, handle: str, title: str, description: str, thumbnails: list[str]):
        self.id: str = id
        self.handle: str = handle
        self.title: str = title
        self.description: str = description
        self.thumbnails: list[str] = thumbnails

    def uploads_playlist(self):
        return f"UU{self.id[2:]}"

    def shorts_playlist(self):
        return f"UUSH{self.id[2:]}"
    
    def to_json(self) -> str:
        return json.dumps({
            "id": self.id,
            "handle": self.handle,
            "title": self.title,
            "description": self.description,
            "thumbnails": self.thumbnails,
        })
    
    @classmethod
    def from_dict(cls, data) -> Self:
        return cls(
            data["id"],
            data["handle"],
            data["title"],
            data["description"],
            data["thumbnails"],
        )
