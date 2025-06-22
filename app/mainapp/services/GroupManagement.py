from typing import List
from datetime import datetime
import uuid

from mainapp.objects.exceptions import (
    DailyFavouriteDBObjectNotFound,
    DailyFavouriteDBWrongObjectType,
)
from mainapp.objects.dtos import UserDTO, GroupDTO, PostDTO, MembershipDTO, RoleEnum
from mainapp.objects.dto_enums import DTOEnum
from mainapp.services.database import DatabaseManagement
from mainapp.services.PostManagement import PostManagement


class GroupManagement:
    user: UserDTO

    def __init__(self, user: UserDTO) -> None:
        self.user = user

    def getGroup(self, id: int) -> GroupDTO:
        obj = DatabaseManagement(self.user).get(id, DTOEnum.GROUP)
        if not obj.is_public and not self.userIsMemberOfGroup(obj):
            raise PermissionError("Access denied to private group.")
        if type(obj) is GroupDTO:
            return obj
        raise DailyFavouriteDBWrongObjectType(GroupDTO, type(obj))

    def listGroups(self) -> List[GroupDTO]:
        try:
            return DatabaseManagement(self.user).list(True, DTOEnum.GROUP, "is_public")
        except DailyFavouriteDBObjectNotFound:
            return []

    def listGroupsWhereUserIsMember(self) -> List[GroupDTO]:
        try:
            memberships = DatabaseManagement(self.user).list(
                self.user.id, DTOEnum.MEMBERSHIP, "user_id"
            )
        except DailyFavouriteDBObjectNotFound:
            return []

        groups = []
        for m in memberships:
            if type(m) is not MembershipDTO:
                raise DailyFavouriteDBWrongObjectType(MembershipDTO, type(m))
            groups.append(m.group)
        return groups

    def createGroup(self, group: GroupDTO) -> None:
        group.admin = self.user
        DatabaseManagement(self.user).get_or_create(group, DTOEnum.GROUP)
        membership = MembershipDTO(None, self.user, group, RoleEnum.OWNER.value)
        DatabaseManagement(self.user).get_or_create(membership, DTOEnum.MEMBERSHIP)

    def updateGroup(self, group: GroupDTO) -> None:
        if group.admin.id != self.user.id:
            raise PermissionError("User not authorized to update group.")
        DatabaseManagement(self.user).create_or_update(group, DTOEnum.GROUP)

    def deleteGroup(self, group: GroupDTO) -> None:
        if group.admin.id != self.user.id:
            raise PermissionError("User not authorized to delete group.")

        try:
            memberships = DatabaseManagement(self.user).list(
                group.id, DTOEnum.MEMBERSHIP, "group_id"
            )
            for m in memberships:
                DatabaseManagement(self.user).delete(m, DTOEnum.MEMBERSHIP)
        except DailyFavouriteDBObjectNotFound:
            pass

        try:
            posts = DatabaseManagement(self.user).list(
                group.id, DTOEnum.POST, "group_id"
            )
            for p in posts:
                DatabaseManagement(self.user).delete(p, DTOEnum.POST)
        except DailyFavouriteDBObjectNotFound:
            pass

        DatabaseManagement(self.user).delete(group, DTOEnum.GROUP)

    def joinGroup(self, group: GroupDTO, password: str | None = None) -> None:
        if (
            not group.is_public
            and hasattr(group, "password")
            and group.password
            and group.password != password
        ):
            raise PermissionError("Incorrect password.")

        try:
            memberships = DatabaseManagement(self.user).list(
                group.id, DTOEnum.MEMBERSHIP, "group_id"
            )
        except DailyFavouriteDBObjectNotFound:
            memberships = []

        for m in memberships:
            if type(m) is MembershipDTO and m.user.id == self.user.id:
                return

        membership = MembershipDTO(None, self.user, group, RoleEnum.MEMBER.value)
        DatabaseManagement(self.user).get_or_create(membership, DTOEnum.MEMBERSHIP)

    def leaveGroup(self, group: GroupDTO) -> None:
        try:
            memberships = DatabaseManagement(self.user).list(
                group.id, DTOEnum.MEMBERSHIP, "group_id"
            )
        except DailyFavouriteDBObjectNotFound:
            return

        for m in memberships:
            if type(m) is MembershipDTO and m.user.id == self.user.id:
                DatabaseManagement(self.user).delete(m, DTOEnum.MEMBERSHIP)
                return

    def getMembers(self, group: GroupDTO) -> List[UserDTO]:
        if not group.is_public and not self.userIsMemberOfGroup(group):
            raise PermissionError("Access denied to private group members.")

        try:
            memberships = DatabaseManagement(self.user).list(
                group.id, DTOEnum.MEMBERSHIP, "group_id"
            )
        except DailyFavouriteDBObjectNotFound:
            return []

        users = []
        for m in memberships:
            if type(m) is not MembershipDTO:
                raise DailyFavouriteDBWrongObjectType(MembershipDTO, type(m))
            users.append(m.user)
        return users

    def userIsMemberOfGroup(self, group: GroupDTO, user: UserDTO | None = None) -> bool:
        if user is None:
            user = self.user

        try:
            memberships = DatabaseManagement(self.user).list(
                group.id, DTOEnum.MEMBERSHIP, "group_id"
            )
        except DailyFavouriteDBObjectNotFound:
            return False

        return any(
            type(m) is MembershipDTO and m.user.id == user.id for m in memberships
        )

    def removeUserFromGroup(self, group: GroupDTO, user: UserDTO) -> None:
        try:
            memberships = DatabaseManagement(self.user).list(
                group.id, DTOEnum.MEMBERSHIP, "group_id"
            )
        except DailyFavouriteDBObjectNotFound:
            return

        for m in memberships:
            if type(m) is MembershipDTO and m.user.id == user.id:
                DatabaseManagement(self.user).delete(m, DTOEnum.MEMBERSHIP)
                return

    def createPost(self, post: PostDTO) -> None:
        if (
            post.group.post_permission == "admin"
            and post.group.admin.id != self.user.id
        ):
            raise PermissionError("Post permission denied.")

        PostManagement(self.user).createPost(post)
        self.syncPostToArchiveGroup(post)

    def deletePost(self, post: PostDTO) -> None:
        if post.user.id != self.user.id and post.group.admin.id != self.user.id:
            raise PermissionError("Delete permission denied.")
        PostManagement(self.user).deletePost(post)

    def createPrivateArchiveGroupIfNotExists(self) -> None:
        archive_identifier = f"archive-{self.user.id}"

        try:
            groups = DatabaseManagement(self.user).list(
                archive_identifier, DTOEnum.GROUP, "description"
            )
            for g in groups:
                if not g.is_public and g.admin.id == self.user.id:
                    return
        except DailyFavouriteDBObjectNotFound:
            pass

        archive = GroupDTO(
            id=None,
            name=str(uuid.uuid4()),
            created_at=datetime.now(),
            description=archive_identifier,
            profile_image=None,
            genre="gemischt",
            is_public=False,
            max_posts_per_day=9999,
            post_permission="admin",
            read_permission="admin",
            admin=self.user,
        )

        DatabaseManagement(self.user).get_or_create(archive, DTOEnum.GROUP)

        membership = MembershipDTO(None, self.user, archive, "archive_viewer")
        DatabaseManagement(self.user).get_or_create(membership, DTOEnum.MEMBERSHIP)

    def syncPostToArchiveGroup(self, post: PostDTO) -> None:
        """
        Fügt den Post zusätzlich zur persönlichen Archivgruppe des Users hinzu.
        """
        archive_group_name = f"{post.user.username}-archive-{post.user.id}"
        try:
            groups = DatabaseManagement(self.user).list(
                archive_group_name, DTOEnum.GROUP, "name"
            )
            archive_group = next(
                g for g in groups if not g.is_public and g.admin.id == post.user.id
            )
        except DailyFavouriteDBObjectNotFound:
            return

        archive_post = PostDTO(
            id=None,
            user=post.user,
            group=archive_group,
            music=post.music,
            posted_at=post.posted_at,
        )
        PostManagement(post.user).createPost(archive_post)
