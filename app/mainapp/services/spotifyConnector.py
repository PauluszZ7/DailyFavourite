from dotenv import load_dotenv
from typing import List, Tuple
import os
import requests
import base64
from mainapp.objects.dtos import MusicDTO

load_dotenv(dotenv_path="../static/.env.local")


class SpotifyConnector:
    _access_token: str | None
    _SPOTIFY_CLIENT: str | None = os.getenv("SPOTIFY_CLIENT")
    _SPOTIFY_SECRET: str | None = os.getenv("SPOTIFY_SECRET")

    def __init__(self) -> None:
        self._access_token = self._get_access_token()

    def _get_access_token(self) -> str:
        auth_str = f"{self._SPOTIFY_CLIENT}:{self._SPOTIFY_SECRET}"
        b64_auth_str = base64.b64encode(auth_str.encode()).decode()

        response = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization": f"Basic {b64_auth_str}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={"grant_type": "client_credentials"},
        )
        response.raise_for_status()  # was für hochwerfen @Lauryn13

        return response.json().get("access_token")

    def get_Track(self, track_id: str) -> MusicDTO:
        url = f"https://api.spotify.com/v1/tracks/{track_id}"
        response = requests.get(
            url, headers={"Authorization": f"Bearer {self._access_token}"}
        )

        # if response.status_code == 404:
        # raise SpotifyTrackNotFoundException(
        #     f"Spotify Track mit ID {track_id} nicht gefunden."
        # )
        response.raise_for_status()

        data = response.json()

        return MusicDTO(
            id=data["id"],
            name=data["name"],
            artist=", ".join([artist["name"] for artist in data["artists"]]),
            album=data["album"]["name"] if "album" in data else None,
            image_url=(
                data["album"]["images"][0]["url"] if data["album"]["images"] else None
            ),
            preview_url=data.get("preview_url"),
            song_url=data.get("external_urls", {}).get("spotify"),
        )

    def search_music_title(
        self, name: str, max_results: int = 3
    ) -> List[Tuple[str, str]]:
        response = requests.get(
            "https://api.spotify.com/v1/search",
            headers={"Authorization": f"Bearer {self._access_token}"},
            params={
                "q": name,
                "type": "track",
                "limit": max_results,
            },
        )
        response.raise_for_status()

        data = response.json()
        results = []
        for item in data.get("tracks", {}).get("items", []):
            results.append((item["id"], item["name"]))
        return results
