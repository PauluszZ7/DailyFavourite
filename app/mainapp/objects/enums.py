from enum import Enum


class RoleEnum(str, Enum):
    OWNER = "owner"
    MODERATOR = "moderator"
    MEMBER = "member"
    ARCHIVE_VIEWER = "archive_viewer"

    @classmethod
    def validate(cls, role: str) -> str:
        if role not in cls._value2member_map_:
            raise ValueError(f"Invalid role: {role}")
        return role


class GenreEnum(str, Enum):
    ROCK = "rock"
    # ALLE GENRES noch hinzufügen

    @classmethod
    def validate(cls, genre: str) -> str:
        if genre not in cls._value2member_map_:
            raise ValueError(f"Invalid role: {genre}")
        return genre
