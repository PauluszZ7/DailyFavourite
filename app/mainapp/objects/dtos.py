from dataclasses import dataclass


@dataclass
class TrackDTO:
    id: str
    name: str
    artist: str
    album: str

    image_url: str | None
    preview_url: str | None
    song_url: str | None
