from typing import Any

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from mainapp.objects.enums import DTOEnum
from mainapp.services.database import DatabaseManagement
from mainapp.objects.dtos import UserDTO
from mainapp.objects.exceptions import (
    DailyFavouriteNoUserFound,
    DailyFavouriteNoUserLoggedIn,
)


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

    def getCurrentUser(self) -> UserDTO:
        """
        Gibt das User-Objekt des aktuell eingeloggten Users zurück.
        NUR GEWOLLT UND MIT BEDACHT NUTZEN!

        (Falls das jemand jemals liest: Ja die Funktion ist sehr unnötig ich weiß :) )
        """
        if self.checkIsLoggedIn():
            user_model = self.request.user
            user_dto = DatabaseManagement(None).get(user_model.id, DTOEnum.USER)
            return user_dto
        else:
            raise DailyFavouriteNoUserLoggedIn()

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

    def register(self, username, password, dto: UserDTO) -> None:
        """
        Registriert einen neuen Nutzer

        Args:
            username (string): Nutzername
            password (string): Password des Nutsers (RAW)
        """
        user = User.objects.create_user(username, password=password)
        user.save()
        dto.id = user.id
        DatabaseManagement(dto).get_or_create(dto, DTOEnum.USER)

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
