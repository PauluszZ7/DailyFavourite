from mainapp.models import Music, User, Post
from mainapp.objects.dtos import TrackDTO
from mainapp.objects.exceptions import (
    TrackSaveException,
    UserNotFoundException,
    InvalidTrackDTOException,
)
from django.db import IntegrityError


def validate_track_dto(track_dto: TrackDTO):
    # überprüfen fehlende felder und so
    if not track_dto.id or not track_dto.name or not track_dto.artist:
        raise InvalidTrackDTOException("TrackDTO ist unvollständig oder ungültig")


def create_or_update_track(track_dto: TrackDTO):
    try:
        validate_track_dto(track_dto)
        track, created = Music.objects.update_or_create(
            id=track_dto.id,
            defaults={
                "name": track_dto.name,
                "artist": track_dto.artist,
                "album": track_dto.album,
                "image_url": track_dto.image_url,
                "preview_url": track_dto.preview_url,
            },
        )
        return track
    except IntegrityError as e:
        raise TrackSaveException(f"Fehler beim Speichern des Tracks: {e}")
    except InvalidTrackDTOException:
        raise


def get_user_favourites(user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise UserNotFoundException(f"User mit ID {user_id} wurde nicht gefunden")

    # lauryn fragen wegen logik
    posts = Post.objects.filter(user=user).select_related("music")
    favourites = [post.music for post in posts]
    return favourites
