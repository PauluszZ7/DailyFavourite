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
