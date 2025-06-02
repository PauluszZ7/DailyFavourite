from typing import Any


class DailyFavouriteBaseException(Exception):
    """
    Base Exception für unser Projekt.

    Attributes:
        status: Fehlerstatus der Exception
        message: Fehlermeldung als Klartext
        context: Zusätslich wichtige Informationen zur Fehlerbehebung
    """

    status: int
    message: str
    context: Any

    def __init__(self, status, message, context: Any = None, *args: object) -> None:
        super().__init__(message, *args)

        self.context = context
        self.status = status
        self.context = context


class DailyFavouriteNoUserFound(DailyFavouriteBaseException):

    def __init__(self, username):
        message = "No user found with matching credentials"
        context = {"username": username}
        super().__init__(404, message, context)


class DailyFavouriteNoUserLoggedIn(DailyFavouriteBaseException):

    def __init__(self):
        message = "Currently no User is logged in."
        context = {"messag": "Currently no user is logged in."}
        super().__init__(500, message, context)


class TrackSaveException(Exception):
    pass


class UserNotFoundException(Exception):
    pass


class InvalidTrackDTOException(Exception):
    pass


class SpotifyTrackNotFoundException(Exception):
    pass


class InvalidTrackDataException(Exception):
    pass
