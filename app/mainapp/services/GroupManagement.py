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

    # Check Permissions ÜBERALL
    # MAXPOSTSPERDAY einbauen beim Post erstellen1
    # ListGroups darf archive groups nicht beinhalten (is_public muss raus da man ja mit Passwort auch private gruppen joinen kann)0.5
    # deletePost muss auch archive Post deleten1
    # password für die Gruppen richtig einbauen (models etc sollten jetzt da sein)1

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
            groups.append(DatabaseManagement(self.user).get(m.group, DTOEnum.GROUP))
        return groups

    def createGroup(self, group: GroupDTO) -> None:
        group.admin = self.user
        DatabaseManagement(self.user).get_or_create(group, DTOEnum.GROUP)
        membership = MembershipDTO(None, self.user, group, RoleEnum.OWNER)
        DatabaseManagement(self.user).get_or_create(membership, DTOEnum.MEMBERSHIP)

    def updateGroup(self, group: GroupDTO) -> None:
        if isinstance(group.admin, int):
            admin_id = group.admin
        elif isinstance(group.admin, UserDTO):
            admin_id = group.admin.id
        else:
            raise DailyFavouriteDBWrongObjectType(UserDTO, type(group.admin))

        if admin_id != self.user.id:
            raise PermissionError("User not authorized to update group.")
        DatabaseManagement(self.user).create_or_update(group, DTOEnum.GROUP)

    def deleteGroup(self, group: GroupDTO) -> None:
        if isinstance(group.admin, int):
            admin_id = group.admin
        elif isinstance(group.admin, UserDTO):
            admin_id = group.admin.id
        else:
            raise DailyFavouriteDBWrongObjectType(UserDTO, type(group.admin))

        if admin_id != self.user.id:
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
            and not self.userIsMemberOfGroup(group)
            and (group.password is None or group.password == "")
            and (password is None or password == "")
        ):
            raise PermissionError("Incorrect password.")

        try:
            memberships = DatabaseManagement(self.user).list(
                group.id, DTOEnum.MEMBERSHIP, "group_id"
            )
        except DailyFavouriteDBObjectNotFound:
            memberships = []

        for m in memberships:
            if type(m) is MembershipDTO and m.user == self.user.id:
                return

        membership = MembershipDTO(None, self.user, group, RoleEnum.MEMBER)
        DatabaseManagement(self.user).get_or_create(membership, DTOEnum.MEMBERSHIP)

    def leaveGroup(self, group: GroupDTO) -> None:
        try:
            memberships = DatabaseManagement(self.user).list(
                group.id, DTOEnum.MEMBERSHIP, "group_id"
            )
        except DailyFavouriteDBObjectNotFound:
            return

        for m in memberships:
            if type(m) is MembershipDTO and m.user == self.user.id:
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
            users.append(DatabaseManagement(self.user).get(m.user, DTOEnum.USER))
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

        return any(type(m) is MembershipDTO and m.user == user.id for m in memberships)

    def removeUserFromGroup(self, group: GroupDTO, user: UserDTO) -> None:
        try:
            memberships = DatabaseManagement(self.user).list(
                group.id, DTOEnum.MEMBERSHIP, "group_id"
            )
        except DailyFavouriteDBObjectNotFound:
            return

        for m in memberships:
            if type(m) is MembershipDTO and m.user == user.id:
                DatabaseManagement(self.user).delete(m, DTOEnum.MEMBERSHIP)
                return

    def createPost(self, post: PostDTO) -> None:
        MAXPOSTSPERDAY = post.group.max_posts_per_day
        if MAXPOSTSPERDAY > 0:
            posts_today = PostManagement(self.user).countPostsToday(post.group)
            if posts_today >= MAXPOSTSPERDAY:
                raise PermissionError(
                    f"Maximum number of posts per day ({MAXPOSTSPERDAY}) reached."
                )
        if (
            post.group.post_permission == "admin"
            and post.group.admin.id != self.user.id
        ):
            raise PermissionError("Post permission denied.")

        post.user = self.user

        PostManagement(self.user).createPost(post)
        self.syncPostToArchiveGroup(post)

    def listPosts(self, group: GroupDTO) -> List[PostDTO]:
        if self.user.id in [u.id for u in self.getMembers(group)]:
            return PostManagement(self.user).listPosts(group)
        else:
            raise PermissionError("Reading of Posts denied.")

    def deletePost(self, post: PostDTO) -> None:
        if post.user.id != self.user.id and post.group.admin.id != self.user.id:
            raise PermissionError("Delete permission denied.")
        PostManagement(self.user).deletePost(post)
        self.syncPostToArchiveGroup(post)

    def createPrivateArchiveGroupIfNotExists(self) -> None:
        try:
            memberships = DatabaseManagement(self.user).list(
                "archive_viewer", DTOEnum.MEMBERSHIP, "role"
            )
            for m in memberships:
                if m.user == self.user.id:
                    return None
        except DailyFavouriteDBObjectNotFound:
            pass

        archive = GroupDTO(
            id=None,
            name=str(uuid.uuid4()),
            created_at=datetime.now(),
            description=self._get_archive_name(),
            profile_image=None,
            genre=None,
            is_public=False,
            password=str(self.user.id),
            max_posts_per_day=-1,
            post_permission="admin",
            read_permission="members",
            admin=self.user,
        )

        DatabaseManagement(self.user).get_or_create(archive, DTOEnum.GROUP)

        membership = MembershipDTO(None, self.user, archive, RoleEnum.ARCHIVE_VIEWER)
        DatabaseManagement(self.user).get_or_create(membership, DTOEnum.MEMBERSHIP)

    def syncPostToArchiveGroup(self, post: PostDTO) -> None:
        """
        Fügt den Post zusätzlich zur persönlichen Archivgruppe des Users hinzu.
        """
        self.createPrivateArchiveGroupIfNotExists()

        try:
            memberships = DatabaseManagement(self.user).list(
                "archive_viewer", DTOEnum.MEMBERSHIP, "role"
            )
            for m in memberships:
                if m.user == self.user.id:
                    archive_group = DatabaseManagement(self.user).get(
                        m.group, DTOEnum.GROUP
                    )
                    break

        except DailyFavouriteDBObjectNotFound:
            return

        if archive_group is None:
            raise DailyFavouriteDBObjectNotFound(DTOEnum.GROUP, id=-1)

        archive_post = PostDTO(
            id=None,
            user=post.user,
            group=archive_group,
            music=post.music,
            posted_at=post.posted_at,
        )
        PostManagement(post.user).createPost(archive_post)

    def _get_archive_name(self) -> str:
        return f"archive-{self.user.id}"
