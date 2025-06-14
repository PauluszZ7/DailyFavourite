from dataclasses import dataclass
from typing import Any
from datetime import datetime


@dataclass
class ModelDTO:
    id: int | str


@dataclass
class UserDTO(ModelDTO):
    username: str
    profile_picture: Any
    favorite_artist: str | None
    favorite_genre: str | None


@dataclass
class GroupDTO(ModelDTO):
    name: str
    created_at: datetime
    description: str

    # settings
    is_public: bool
    max_posts_per_day: bool
    post_permission: str
    read_permission: str


@dataclass
class MusicDTO(ModelDTO):
    name: str
    artist: str
    album: str

    image_url: str | None
    preview_url: str | None
    song_url: str | None


@dataclass
class PostDTO(ModelDTO):
    user: UserDTO
    group: GroupDTO
    music: MusicDTO
    posted_at: datetime


@dataclass
class CommentDTO(ModelDTO):
    user: UserDTO
    post: PostDTO
    content: str
    created_at: datetime


@dataclass
class VoteDTO(ModelDTO):
    user: UserDTO
    post: PostDTO
    is_upvote: bool
