from mainapp.objects.dtos import TrackDTO
from mainapp.services.database import DatabaseManagement

import pytest

@pytest.mark.django_db
class TestDatabase:
    USER_ID = 12345

    def test_create_music(self):
        music_id = "1234"

        music = fetch_spotify_track(music_id)

        dbm = DatabaseManagement(self.USER_ID)
        dbm.create_or_update_music(music)
        music = dbm.get_music(id=music.id)
        
        assert music is not None
        assert music.id == music_id



    # def test_get_user_posted_music(self):
    #     pass




def fetch_spotify_track(id:str) -> TrackDTO:
    # Temporäres Dummy-Return bis Spotify-Integration steht
    return TrackDTO(
        id=id,
        name="Fake Song",
        artist="Fake Artist",
        album="Fake Album",
        image_url="http://example.com/image.jpg",
        preview_url="http://example.com/preview.mp3",
        song_url="http://example.com/song",
    )
