from typing import Any

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from mainapp.objects.exceptions import DailyFavouriteNoUserFound


class UserManagement:
    """
    Dient zur Verwaltung der Nutzerobjekte.

    Benötigt immer die aktulle request um Arbeiten zu können!
    """

    request: Any

    def __init__(self, request) -> None:
        """
        Args:
            request (Request): Request der aktuellen Anfrage
        """
        self.request = request

    def login(self, username: str, password: str) -> None:
        """
        Validiert die Nutzerdaten und loggt den Nutzer anschließend ein.

        Args:
            username (string): Nutzername
            password (string): Password des Nutzers (RAW)
        """
        user = authenticate(username=username, password=password)
        if user is None:
            raise DailyFavouriteNoUserFound(username=username)

        login(self.request, user)

    def logout(self) -> None:
        """
        Loggt den aktuellen Nutzer aus.
        """
        logout(self.request)

    def register(self, username, password) -> None:
        """
        Registriert einen neuen Nutzer

        Args:
            username (string): Nutzername
            password (string): Password des Nutsers (RAW)
        """
        user = User.objects.create_user(username, password=password)
        user.save()

    def checkIsLoggedIn(self) -> bool:
        """
        Überprüft ob ein Nutzer eingeloggt ist.

        Returns:
            bool: Ist der Nutzer eingeloggt.
        """
        return self.request.user.is_authenticated

    def changeUserPassword(
        self, username: str, old_password: str, new_password: str
    ) -> None:
        """
        Ändert das Passwort für einen Nutzer.

        Args:
            username (string): Nutzername
            password (string): Password des Nutsers (RAW)
        """
        user = authenticate(username=username, password=old_password)

        if user is not None:
            user.set_password(new_password)
            user.save()

    def deleteUser(self, password: str) -> None:
        """
        Löscht den im moment eingeloggten User.

        Args:
            password (string): Password des Nutzers (zur Authentifizierung)
        """
        user = authenticate(username=self.request.user.username, password=password)
        user.delete()
