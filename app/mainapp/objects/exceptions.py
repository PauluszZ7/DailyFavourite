from typing import Any

from mainapp.objects.dtos import ModelDTO


class DailyFavouriteBaseException(Exception):
    """
    Base Exception für unser Projekt.

    Attributes:
        status: Fehlerstatus der Exception
        message: Fehlermeldung als Klartext
        context: Zusätzlich wichtige Informationen zur Fehlerbehebung
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


class DailyFavouriteMinimumRequiredParameter(DailyFavouriteBaseException):

    def __init__(self, function_name, description) -> None:
        message = "Function needs a minimum of given Parameters. See Details"
        context = {"function_name": function_name, "description": description}
        super().__init__(500, message, context)


class DailyFavouriteAlreadyVotedForPost(DailyFavouriteBaseException):

    def __init__(self):
        message = "User has already voted for the post."
        context = {}
        super().__init__(500, message, context)


class DailyFavouriteUserAlreadyInGroup(DailyFavouriteBaseException):

    def __init__(self):
        message = "User is already within this group."
        context = {}
        super().__init__(500, message, context)


class DailyFavouritePrivateGroupMustContainPassword(DailyFavouriteBaseException):

    def __init__(self):
        message = "Could not create Group, because not password was set."
        context = {}
        super().__init__(500, message, context)


class DailyFavouriteMaxPostsPerDayReached(DailyFavouriteBaseException):

    def __init__(self, group_id, max_posts):
        message = "User has reached maximum amount of allowed posts per day."
        context = {"group_id": group_id, "max_posts": max_posts}
        super().__init__(403, message, context)


class DailyFavouriteUnallowedRoleAssignment(DailyFavouriteBaseException):

    def __init__(self):
        message = (
            "You are not allowed to change the userroles to: admin, archive_viewer"
        )
        context = {}
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


class DailyFavouriteDBAttributeNotFound(DailyFavouriteBaseException):

    def __init__(self, type: ModelDTO, attribute: str) -> None:
        message = (
            "Database Object with matching Attribute could not be found. See Details."
        )
        context = {"type": type, "attribute": attribute}
        super().__init__(404, message, context)


class DailyFavouriteDBWrongObjectType(DailyFavouriteBaseException):

    def __init__(self, requested_type, real_type):
        message = "Database returned wrong unexpected object type. See Details"
        context = {"expected": requested_type, "real": real_type}
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
