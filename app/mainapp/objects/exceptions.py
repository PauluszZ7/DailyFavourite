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
        context = {"message": "Currently no user is logged in."}
        super().__init__(500, message, context)


class DailyFavouriteDBObjectNotFound(DailyFavouriteBaseException):

    def __init__(self, type, id) -> None:
        message = "Database Object with matching id was not found. See Details."
        context = {"id": id, "type": type}
        super().__init__(404, message, context)


class DailyFavouriteDBObjectCouldNotBeCreated(DailyFavouriteBaseException):

    def __init__(self, dto, baseException):
        message = "Database Object could not be created. See Details."
        context = {"DTO": dto, "Exception": baseException}
        super().__init__(500, message, context)


class DailyFavouriteSpotifyTrackNotFound(DailyFavouriteBaseException):

    def __init__(self, track_id) -> None:
        message = "Spotify Track was not found."
        context = {"TrackID": track_id}
        super().__init__(404, message, context)


class DailyFavouriteSpotifyInvalidBase62ID(DailyFavouriteBaseException):

    def __init__(self, track_id) -> None:
        message = "Spotify ID is invalid and not a base62 ID"
        context = {"TrackID": track_id}
        super().__init__(400, message, context)
