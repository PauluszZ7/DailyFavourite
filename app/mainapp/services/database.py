from mainapp.models import Music, User, Post
from mainapp.objects.dtos import TrackDTO
from mainapp.objects.exceptions import (
    TrackSaveException,
    UserNotFoundException,
    InvalidTrackDTOException,
)
from django.db import IntegrityError


class DatabaseManagement:
    current_user:str

    def __init__(self, current_user) -> None:
        self.current_user = current_user

    def get_music(self, id:str) -> TrackDTO:
        music = Music.objects.get(id=id)
        return TrackDTO(
            id=music.id,
            name=music.name,
            artist=music.artist,
            album=music.album,
            image_url=music.image_url,
            preview_url=music.preview_url,
            song_url=music.song_url,
        )

    def delete_music(self, music:TrackDTO) -> None:
        pass

    # def get_comment(self, id:str) -> CommentDTO:
    #     pass

    def get_user_posted_music(self):
        try:
            user = User.objects.get(id=self.current_user)
        except User.DoesNotExist:
            raise UserNotFoundException(f"User mit ID {self.current_user} wurde nicht gefunden")

        # lauryn fragen wegen logik
        posts = Post.objects.filter(user=user).select_related("music")
        favourites = [post.music for post in posts]
        return favourites




    def create_or_update_music(self, track_dto: TrackDTO):
        try:
            track, created = Music.objects.update_or_create(
                id=track_dto.id,
                defaults={
                    "name": track_dto.name,
                    "artist": track_dto.artist,
                    "album": track_dto.album,
                    "image_url": track_dto.image_url,
                    "preview_url": track_dto.preview_url,
                    "song_url": track_dto.song_url,
                },
            )
            return track
        except IntegrityError as e:
            raise TrackSaveException(f"Fehler beim Speichern des Tracks: {e}")
        except InvalidTrackDTOException:
            raise



