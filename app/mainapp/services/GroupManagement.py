from typing import List
from datetime import datetime, timedelta
import uuid

from mainapp.objects.exceptions import (
    DailyFavouriteDBObjectNotFound,
    DailyFavouriteDBWrongObjectType,
    DailyFavouriteMaxPostsPerDayReached,
    DailyFavouriteMinimumRequiredParameter,
    DailyFavouriteUnallowedRoleAssignment,
    DailyFavouriteUserAlreadyInGroup,
    DailyFavouritePrivateGroupMustContainPassword,
)
from mainapp.objects.dtos import UserDTO, GroupDTO, PostDTO, MembershipDTO, RoleEnum
from mainapp.objects.dto_enums import DTOEnum
from mainapp.services.database import DatabaseManagement
from mainapp.services.PostManagement import PostManagement


class GroupManagement:
    user: UserDTO

    def __init__(self, user: UserDTO) -> None:
        self.user = user
        self.createPrivateArchiveGroupIfNotExists()

    def getGroup(self, id: int) -> GroupDTO:
        obj = DatabaseManagement(self.user).get(id, DTOEnum.GROUP)
        if not obj.is_public and not self.userIsMemberOfGroup(obj):
            raise PermissionError("Access denied to private group.")
        if type(obj) is GroupDTO:
            return obj
        raise DailyFavouriteDBWrongObjectType(GroupDTO, type(obj))

    def listGroups(self, show_archives: bool = False) -> List[GroupDTO]:
        try:
            if show_archives:
                return DatabaseManagement(self.user).list_all(DTOEnum.GROUP)

            memberships = DatabaseManagement(self.user).list(
                "archive_viewer", DTOEnum.MEMBERSHIP, "role"
            )
            archive_groups = []
            groups_without_archive = []

            for m in memberships:
                archive_groups.append(
                    DatabaseManagement(self.user).get(m.group, DTOEnum.GROUP)
                )
            groups = DatabaseManagement(self.user).list_all(DTOEnum.GROUP)

            for g in groups:
                if g not in archive_groups:
                    groups_without_archive.append(g)

            return groups_without_archive
        except DailyFavouriteDBObjectNotFound as e:
            raise e

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
            if m.role != RoleEnum.ARCHIVE_VIEWER.value:
                groups.append(DatabaseManagement(self.user).get(m.group, DTOEnum.GROUP))
        return groups

    def createGroup(self, group: GroupDTO) -> None:
        if (group.password is None or group.password == "") and not group.is_public:
            raise DailyFavouritePrivateGroupMustContainPassword()

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
        if self.userIsMemberOfGroup(group):
            raise DailyFavouriteUserAlreadyInGroup()
        if (
            not group.is_public
            and (group.password is not None or group.password != "")
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
            if self._get_role_for_group(group=group) == RoleEnum.MEMBER:
                raise PermissionError("Permission for removing a user denied.")
            memberships = DatabaseManagement(self.user).list(
                group.id, DTOEnum.MEMBERSHIP, "group_id"
            )
        except DailyFavouriteDBObjectNotFound:
            return

        for m in memberships:
            if type(m) is MembershipDTO and m.user == user.id:
                DatabaseManagement(self.user).delete(m, DTOEnum.MEMBERSHIP)
                return

    def changeUserRole(self, group: GroupDTO, user: UserDTO, role: RoleEnum):
        try:
            if self.user.id != group.admin.id:
                raise PermissionError("Only Admins are allowed to change User Roles.")

            if not self.userIsMemberOfGroup(group, user):
                raise DailyFavouriteDBObjectNotFound(
                    DTOEnum.GROUP, group.id
                )  # Ergibt eigentlich keinen Sinn so

            if role == RoleEnum.ARCHIVE_VIEWER or role == RoleEnum.OWNER:
                raise DailyFavouriteUnallowedRoleAssignment()

            if role == self._get_role_for_group(group=group, user=user):
                return None

            memberships = DatabaseManagement(self.user).list(
                group.id, DTOEnum.MEMBERSHIP, "group_id"
            )
        except DailyFavouriteDBObjectNotFound:
            return

        for m in memberships:
            if type(m) is MembershipDTO and m.user == user.id:
                if role == m.role:
                    break

                m.role = role.value
                m.user = DatabaseManagement(self.user).get(m.user, DTOEnum.USER)
                m.group = DatabaseManagement(self.user).get(m.group, DTOEnum.GROUP)
                DatabaseManagement(self.user).create_or_update(m, DTOEnum.MEMBERSHIP)
                return

        raise DailyFavouriteDBObjectNotFound(DTOEnum.MEMBERSHIP, -1)

    def createPost(self, post: PostDTO) -> None:
        if post.group is None:
            # Profilpost (Archive)
            post.user = self.user
            post.posted_at = datetime.now()
            self.syncPostToArchiveGroup(post)
            return None
        max_posts = post.group.max_posts_per_day
        current_role = self._get_role_for_group(post=post)
        if max_posts > 0:
            posts_today = self._count_todays_posts(post.group)
            if posts_today >= max_posts:
                raise DailyFavouriteMaxPostsPerDayReached(post.group.id, max_posts)
        if (
            post.group.post_permission == RoleEnum.OWNER.value
            and post.group.admin.id != self.user.id
        ):
            raise PermissionError("Post permission denied.")
        if (
            post.group.post_permission == RoleEnum.MODERATOR.value
            and current_role == RoleEnum.MEMBER
        ):
            raise PermissionError("Post permission denied")

        post.user = self.user
        post.posted_at = datetime.now()

        PostManagement(self.user).createPost(post)
        self.syncPostToArchiveGroup(post)

    def listPosts(self, group: GroupDTO) -> List[PostDTO]:
        if self.user.id in [u.id for u in self.getMembers(group)]:
            return PostManagement(self.user).listPosts(group)
        else:
            raise PermissionError("Reading of Posts denied.")

    def deletePost(self, post: PostDTO) -> None:
        current_role = self._get_role_for_group(post=post)
        if (
            post.user.id != self.user.id
            and post.group.admin.id != self.user.id
            and current_role != RoleEnum.MODERATOR
        ):
            raise PermissionError("Delete permission denied.")
        if (
            current_role == RoleEnum.MODERATOR
            and post.group.post_permission == RoleEnum.OWNER.value
        ):
            raise PermissionError("Delete permission denied.")
        PostManagement(self.user).deletePost(post)
        if post.user.id == self.user.id:
            archive_post = self._get_archive_post(post)
            PostManagement(self.user).deletePost(archive_post)
        else:
            user = DatabaseManagement(self.user).get(post.user.id, DTOEnum.USER)
            archive_post = GroupManagement(user)._get_archive_post(post)
            PostManagement(self.user).deletePost(archive_post)

    def get_archive(self) -> GroupDTO:
        memberships = DatabaseManagement(self.user).list(
            "archive_viewer", DTOEnum.MEMBERSHIP, "role"
        )
        for m in memberships:
            if m.user == self.user.id:
                archive_group = DatabaseManagement(self.user).get(
                    m.group, DTOEnum.GROUP
                )
                break
        return archive_group

    def createPrivateArchiveGroupIfNotExists(self) -> None:
        try:
            memberships = DatabaseManagement(self.user).list(
                "archive_viewer", DTOEnum.MEMBERSHIP, "role"
            )
            for m in memberships:
                if m.user == self.user.id:
                    return
        except DailyFavouriteDBObjectNotFound:
            pass

        name_id = str(uuid.uuid4())
        archive = GroupDTO(
            id=None,
            name=name_id,
            created_at=datetime.now(),
            description=self._get_archive_name(),
            profile_image=None,
            genre=None,
            is_public=False,
            password=str(self.user.id),
            max_posts_per_day=-1,
            post_permission=RoleEnum.OWNER.value,
            read_permission="members",
            admin=self.user,
        )

        DatabaseManagement(self.user).get_or_create(archive, DTOEnum.GROUP)
        # 1.5h debugging für diese kacke hier
        archive = DatabaseManagement(self.user).list_all(DTOEnum.GROUP)
        for a in archive:
            if a.name == name_id:
                archive = a
                break
        if isinstance(archive, list):
            raise DailyFavouriteDBObjectNotFound(DTOEnum.GROUP, name_id)

        membership = MembershipDTO(None, self.user, archive, RoleEnum.ARCHIVE_VIEWER)
        DatabaseManagement(self.user).get_or_create(membership, DTOEnum.MEMBERSHIP)

    def syncPostToArchiveGroup(self, post: PostDTO) -> None:
        """
        Fügt den Post zusätzlich zur persönlichen Archivgruppe des Users hinzu.
        """

        try:
            archive_group = self.get_archive()
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

    def _count_todays_posts(self, group: GroupDTO) -> int:
        try:
            user_posts = DatabaseManagement(self.user).list(
                self.user.id, DTOEnum.POST, "user_id"
            )
        except DailyFavouriteDBObjectNotFound:
            return 0

        todays_posts = 0

        for post in user_posts:
            if post.group == group.id and datetime.fromisoformat(
                post.posted_at
            ) >= datetime.today() - timedelta(days=1):
                todays_posts += 1

        return todays_posts

    def _get_archive_post(self, post: PostDTO) -> PostDTO:
        archive = self.get_archive()
        archive_posts = DatabaseManagement(self.user).list(
            archive.id, DTOEnum.POST, "group_id"
        )
        archive_post = None

        post.posted_at = post.posted_at.replace(tzinfo=None)

        for p in archive_posts:
            p.posted_at = datetime.fromisoformat(p.posted_at).replace(tzinfo=None)
            if (p.posted_at == post.posted_at) and (int(p.music) == int(post.music.id)):
                archive_post = p
                break

        if isinstance(archive_post, PostDTO):
            return archive_post
        else:
            raise DailyFavouriteDBObjectNotFound(DTOEnum.POST, -1)

    def _get_role_for_group(
        self,
        post: PostDTO | None = None,
        group: GroupDTO | None = None,
        user: UserDTO | None = None,
    ) -> RoleEnum:
        if post is None and group is None:
            raise DailyFavouriteMinimumRequiredParameter(
                "get_role_for_group", "need at least a post or group."
            )

        if user is None:
            user = self.user

        if group is None:
            group = post.group
            if isinstance(group, int):
                group = DatabaseManagement(user).get(group, DTOEnum.GROUP)

        memberships = DatabaseManagement(user).list(
            user.id, DTOEnum.MEMBERSHIP, "user_id"
        )
        role = None
        for m in memberships:
            if m.group == group.id:
                role = m.role

        if role is not None:
            return RoleEnum(role)
        raise PermissionError("User is not in group and has no permissions.")
