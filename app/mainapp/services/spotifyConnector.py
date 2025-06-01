from dotenv import load_dotenv
from typing import List

from mainapp.objects.dtos import TrackDTO

import os
import requests
import base64

load_dotenv(dotenv_path='../static/.env.local')


class SpotifyConnector:
    _access_token: str | None
    _SPOTIFY_CLIENT:str | None = os.getenv("SPOTIFY_CLIENT")
    _SPOTIFY_SECRET:str | None = os.getenv("SPOTIFY_SECRET")

    def __init__(self) -> None:
        self._access_token = self._get_access_token()

    def search_music_title(self, name:str, max_results:int=3) -> List[(str, str)]:
        response = requests.get(
            'https://api.spotify.com/v1/search',
            headers={'Authorization': f'Bearer {self._access_token}'},
            params={
                'q': name,
                'type': 'artist',
                'limit': max_results,
            }
        )

    def get_Track(self, track_id:str) -> TrackDTO:
        pass


    def _get_access_token(self) -> str:
        auth_str = f'{self._SPOTIFY_CLIENT}:{self._SPOTIFY_SECRET}'
        b64_auth_str = base64.b64encode(auth_str.encode()).decode()

        response = requests.post(
            'https://accounts.spotify.com/api/token',
            headers={
                'Authorization': f'Basic {b64_auth_str}',
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            data={'grant_type': 'client_credentials'}
        )

        return response.json().get('access_token')
  

