import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware

from mainapp.models import Post
from mainapp.services.GroupManagement import GroupManagement
from mainapp.services.database import DatabaseManagement
from mainapp.services.userManagement import UserManagement
from mainapp.objects.dtos import UserDTO, GroupDTO, PostDTO
from mainapp.objects.dto_enums import DTOEnum
from mainapp.objects.exceptions import DailyFavouriteDBObjectNotFound
from mainapp.tests.helpers import create_dummy_instance

USERNAME = "testuser"
PASSWORD = "testpassword"


@pytest.mark.django_db
class TestGroupManagement:

    @pytest.fixture
    def simRequest(self):
        # sim request
        request = RequestFactory().get("/")
        SessionMiddleware(get_response=lambda x: x).process_request(request)
        AuthenticationMiddleware(lambda r: r).process_request(request)
        request.session.save()

        user = User.objects.create_user(username=USERNAME, password=PASSWORD)
        UserManagement(request).login(USERNAME, PASSWORD)
        DatabaseManagement(None).get_or_create(
            UserDTO(user.id, user.username, None, None, None), DTOEnum.USER
        )
        return request

    @pytest.fixture
    def secondSimUser(self):
        other_user = DatabaseManagement(None).get_or_create(
            UserDTO(2, "other", None, None, None), DTOEnum.USER
        )
        return other_user

    # Tests
    def test_get_create_delete_group(self, simRequest):
        user = UserManagement(simRequest).getCurrentUser()
        assert user is not None

        group_management = GroupManagement(user)
        new_group = create_dummy_instance(GroupDTO)
        new_group.id = 123
        group_management.createGroup(new_group)

        created_group = group_management.getGroup(new_group.id)

        assert isinstance(created_group, GroupDTO)
        assert created_group.admin == user.id

        group_management.deleteGroup(created_group)

        with pytest.raises(DailyFavouriteDBObjectNotFound):
            group_management.getGroup(created_group.id)

    def test_list_groups(self, simRequest):
        user = UserManagement(simRequest).getCurrentUser()
        assert user is not None

        group_management = GroupManagement(user)
        new_group = create_dummy_instance(GroupDTO)
        new_group.id = 123
        group_management.createGroup(new_group)

        new_group = create_dummy_instance(GroupDTO)
        group_management.createGroup(new_group)

        groups = group_management.listGroups()

        assert isinstance(groups, list)
        assert (
            len(groups) == 3
        )  # +1 für archive group (testet daher auch die erstellung dieser Gruppe gleich mit.)
        assert isinstance(groups[0], GroupDTO)
        assert isinstance(groups[1], GroupDTO)

    def test_list_groups_where_user_is_member(self, simRequest, secondSimUser):
        user = UserManagement(simRequest).getCurrentUser()
        assert user is not None

        group_management = GroupManagement(user)
        new_group = create_dummy_instance(GroupDTO)
        new_group.id = 123
        group_management.createGroup(new_group)

        new_group = create_dummy_instance(GroupDTO)
        new_group.id = 124
        group_management.createGroup(new_group)

        other_group = create_dummy_instance(GroupDTO)
        other_group.id = 44

        GroupManagement(secondSimUser).createGroup(other_group)

        groups = group_management.listGroupsWhereUserIsMember()

        assert isinstance(groups, list)
        assert len(groups) == 2
        assert isinstance(groups[0], GroupDTO)
        assert groups[0].id != other_group.id
        assert isinstance(groups[1], GroupDTO)
        assert groups[1].id != other_group.id

    def test_update_group(self, simRequest):
        user = UserManagement(simRequest).getCurrentUser()
        assert user is not None

        group_management = GroupManagement(user)
        group = create_dummy_instance(GroupDTO)
        group.id = 123
        group_management.createGroup(group)

        group.name = "Updated Group Name"
        group_management.updateGroup(group)

        updated_group = group_management.getGroup(group.id)
        assert updated_group.name == "Updated Group Name"

    def test_join_leave_userIsMember_group(self, simRequest, secondSimUser):
        user = UserManagement(simRequest).getCurrentUser()
        assert user is not None

        group_management = GroupManagement(user)
        group = create_dummy_instance(GroupDTO)
        group.id = 123
        group_management.createGroup(group)

        GroupManagement(secondSimUser).joinGroup(group)
        assert GroupManagement(secondSimUser).userIsMemberOfGroup(group)

        GroupManagement(secondSimUser).leaveGroup(group)
        assert not GroupManagement(secondSimUser).userIsMemberOfGroup(group)

    def testjoinPrivateGroup(self, simRequest, secondSimUser):
        pass

    def test_get_members(self, simRequest, secondSimUser):
        user = UserManagement(simRequest).getCurrentUser()
        assert user is not None

        group_management = GroupManagement(user)
        group = create_dummy_instance(GroupDTO)
        group.id = 123
        group_management.createGroup(group)
        GroupManagement(secondSimUser).joinGroup(group)
        members = group_management.getMembers(group)

        assert isinstance(members, list)
        assert len(members) == 2
        assert isinstance(members[0], UserDTO)
        assert members[0].id == user.id
        assert isinstance(members[1], UserDTO)
        assert members[1].id == secondSimUser.id

    def test_remove_user_from_group(self, simRequest, secondSimUser):
        user = UserManagement(simRequest).getCurrentUser()
        assert user is not None

        group_management = GroupManagement(user)
        group = create_dummy_instance(GroupDTO)
        group.id = 123
        group_management.createGroup(group)
        GroupManagement(secondSimUser).joinGroup(group)

        members = group_management.getMembers(group)
        assert len(members) == 2

        group_management.removeUserFromGroup(group, secondSimUser)
        members = group_management.getMembers(group)
        assert len(members) == 1
        assert members[0].id == user.id

    def test_create_sync_delete_Posts(self, simRequest):
        user = UserManagement(simRequest).getCurrentUser()
        assert user is not None

        group_management = GroupManagement(user)
        group = create_dummy_instance(GroupDTO)
        group.id = 123
        group_management.createGroup(group)

        posts_before = len(Post.objects.all())

        post = create_dummy_instance(PostDTO)
        post.id = 122352
        post.group = group
        group_management.createPost(post)
        post2 = create_dummy_instance(PostDTO)
        post2.id = 44
        post2.group = group
        group_management.createPost(post2)
        created_post = group_management.listPosts(group)
        posts_after = len(Post.objects.all())

        assert isinstance(created_post, list)
        assert len(created_post) == 2
        assert isinstance(created_post[0], PostDTO)
        assert created_post[0].group == group.id
        assert created_post[0].user == simRequest.user.id
        # test sync of Posts
        assert posts_before + 2 == (posts_after - posts_before) / 2

        group_management.deletePost(post)
        created_post = group_management.listPosts(group)

        assert isinstance(created_post, list)
        assert len(created_post) == 1
        assert isinstance(created_post[0], PostDTO)

    def test_admin_permissions(self, simRequest, secondSimUser):
        pass

    def test_post_permissions(self, simRequest, secondSimUser):
        pass

    def test_max_post_per_day(self, simRequest):
        pass
