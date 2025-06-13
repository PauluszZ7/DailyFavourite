from typing import List, Tuple
from datetime import datetime

from mainapp.objects.exceptions import (
    DailyFavouriteDBObjectCouldNotBeCreated,
    DailyFavouriteDBObjectNotFound,
    DailyFavouriteDBWrongObjectType,
)
from mainapp.objects.dtos import UserDTO, GroupDTO, MembershipDTO, PostDTO
from mainapp.objects.enums import DTOEnum
from mainapp.services.database import DatabaseManagement
from mainapp.services.PostManagement import PostManagement


class GroupManagement:
    user: UserDTO

    def __init__(self, user: UserDTO) -> None:
        self.user = user

    def getGroup(self, id: int) -> GroupDTO:
        obj = DatabaseManagement(self.user).get(id, DTOEnum.GROUP)
        if isinstance(obj, GroupDTO):
            return obj
        raise DailyFavouriteDBWrongObjectType(GroupDTO, type(obj))

    def createGroup(self, group: GroupDTO) -> None:
        DatabaseManagement(self.user).get_or_create(group, DTOEnum.GROUP)
        membership = MembershipDTO(None, self.user, group)
        DatabaseManagement(self.user).get_or_create(membership, DTOEnum.MEMBERSHIP)

    def updateGroup(self, group: GroupDTO) -> None:
        DatabaseManagement(self.user).create_or_update(group, DTOEnum.GROUP)

    def deleteGroup(self, group: GroupDTO) -> None:
        DatabaseManagement(self.user).delete(group, DTOEnum.GROUP)

    def joinGroup(self, group: GroupDTO) -> None:
        try:
            memberships = DatabaseManagement(self.user).list(group.id, DTOEnum.MEMBERSHIP, "group_id")
        except DailyFavouriteDBObjectNotFound:
            memberships = []

        for m in memberships:
            if isinstance(m, MembershipDTO) and m.user.id == self.user.id:
                return  

        membership = MembershipDTO(None, self.user, group)
        DatabaseManagement(self.user).get_or_create(membership, DTOEnum.MEMBERSHIP)

    def leaveGroup(self, group: GroupDTO) -> None:
        try:
            memberships = DatabaseManagement(self.user).list(group.id, DTOEnum.MEMBERSHIP, "group_id")
        except DailyFavouriteDBObjectNotFound:
            return

        for m in memberships:
            if isinstance(m, MembershipDTO) and m.user.id == self.user.id:
                DatabaseManagement(self.user).delete(m, DTOEnum.MEMBERSHIP)
                return

    def listGroups(self) -> List[GroupDTO]:
        try:
            return DatabaseManagement(self.user).list(True, DTOEnum.GROUP, "is_public")
        except DailyFavouriteDBObjectNotFound:
            return []

    def listGroupsWhereUserIsMember(self) -> List[GroupDTO]:
        try:
            memberships = DatabaseManagement(self.user).list(self.user.id, DTOEnum.MEMBERSHIP, "user_id")
        except DailyFavouriteDBObjectNotFound:
            return []

        groups = []
        for membership in memberships:
            if not isinstance(membership, MembershipDTO):
                raise DailyFavouriteDBWrongObjectType(MembershipDTO, type(membership))
            groups.append(membership.group)
        return groups

    def getMembers(self, group: GroupDTO) -> List[UserDTO]:
        try:
            memberships = DatabaseManagement(self.user).list(group.id, DTOEnum.MEMBERSHIP, "group_id")
        except DailyFavouriteDBObjectNotFound:
            return []

        users = []
        for membership in memberships:
            if not isinstance(membership, MembershipDTO):
                raise DailyFavouriteDBWrongObjectType(MembershipDTO, type(membership))
            users.append(membership.user)
        return users

    def userIsMemberOfGroup(self, group: GroupDTO, user: UserDTO) -> bool:
        try:
            memberships = DatabaseManagement(self.user).list(group.id, DTOEnum.MEMBERSHIP, "group_id")
        except DailyFavouriteDBObjectNotFound:
            return False

        return any(
            isinstance(m, MembershipDTO) and m.user.id == user.id for m in memberships
        )

    def removeUserFromGroup(self, group: GroupDTO, user: UserDTO) -> None:
        try:
            memberships = DatabaseManagement(self.user).list(group.id, DTOEnum.MEMBERSHIP, "group_id")
        except DailyFavouriteDBObjectNotFound:
            return

        for m in memberships:
            if isinstance(m, MembershipDTO) and m.user.id == user.id:
                DatabaseManagement(self.user).delete(m, DTOEnum.MEMBERSHIP)
                return

    def getProfilePicture(self, group: GroupDTO) -> str:
        if group.image_url:
            return group.image_url
        return "https://example.com/default-group-image.png"

    def createPost(self, post: PostDTO) -> None:
        PostManagement(self.user).createPost(post)

    def deletePost(self, post: PostDTO) -> None:
        PostManagement(self.user).deletePost(post)

    def checkUserHasPermission(self, group: GroupDTO) -> bool:
        return self.userIsMemberOfGroup(group, self.user)