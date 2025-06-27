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

    @classmethod
    def get_values(cls):
        return [opt.value for opt in cls if opt != RoleEnum.ARCHIVE_VIEWER] 


class GenreEnum(str, Enum):
    ROCK = "Rock"
    POP = "Pop"
    HIP_HOP = "Hip-Hop"
    ELECTRONIC = "Electronic"
    JAZZ = "Jazz"
    CLASSICAL = "Classical"
    INDIE = "Indie"
    METAL = "Metal"
    FOLK = "Folk"
    SCHLAGER = "Schlager"
    ANDERE = "Andere"
    GEMISCHT = "Gemischt"

    @classmethod
    def validate(cls, genre: str) -> str:
        if genre not in cls._value2member_map_:
            raise ValueError(f"Invalid role: {genre}")
        return genre
    
    @classmethod
    def get_values(cls):
        return [opt.value for opt in cls]
