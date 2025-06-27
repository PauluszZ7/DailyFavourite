import pytest

from django.contrib.auth.models import User
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware

from mainapp.services.GroupManagement import GroupManagement
from mainapp.services.userManagement import UserManagement
from mainapp.services.FriendsManagement import FriendsManagement
from mainapp.services.database import DatabaseManagement
from mainapp.objects.dtos import UserDTO, PostDTO
from mainapp.objects.dto_enums import DTOEnum

from helpers import create_dummy_instance

USERNAME = "testuser"
USERNAME2 = "testuser2"
PASSWORD = "testpassword"


@pytest.mark.django_db
class TestFriendsManagement:

    @pytest.fixture
    def simRequest(self):
        # sim request
        request = RequestFactory().get("/")
        SessionMiddleware(get_response=lambda x: x).process_request(request)
        AuthenticationMiddleware(lambda r: r).process_request(request)
        request.session.save()

        user = User.objects.create_user(username=USERNAME, password=PASSWORD)
        DatabaseManagement(None).get_or_create(
            UserDTO(user.id, user.username, None, None, None), DTOEnum.USER
        )
        user2 = User.objects.create_user(username=USERNAME2, password=PASSWORD)
        DatabaseManagement(None).get_or_create(
            UserDTO(user2.id, user2.username, None, None, None), DTOEnum.USER
        )

        UserManagement(request).login(USERNAME, PASSWORD)
        return request

    def test_list_search_add_delete_friend(self, simRequest):
        user = UserManagement(simRequest).getCurrentUser()
        assert user is not None

        fm = FriendsManagement(user)
        user_list = fm.searchUsers("test")

        assert isinstance(user_list, list)
        assert len(user_list) == 1
        assert user_list[0].id != user.id

        friends_user = user_list[0]
        friends_list = fm.getFriends()

        assert isinstance(friends_list, list)
        assert len(friends_list) == 0

        fm.addFriend(friends_user)
        friends_list = fm.getFriends()

        assert isinstance(friends_list, list)
        assert len(friends_list) == 1
        assert friends_list[0].friend is friends_user.id

        fm.removeFriend(friends_user)
        friends_list = fm.getFriends()

        assert isinstance(friends_list, list)
        assert len(friends_list) == 0

    def test_list_friends_posts(self, simRequest):
        user = UserManagement(simRequest).getCurrentUser()
        assert user is not None

        fm = FriendsManagement(user)
        user2 = fm.searchUsers("test")[0]
        user3 = User.objects.create_user(username="nochEinTest", password=PASSWORD)
        user3 = DatabaseManagement(None).get_or_create(
            UserDTO(user3.id, user3.username, None, None, None), DTOEnum.USER
        )

        post = create_dummy_instance(PostDTO)
        post.group = None
        GroupManagement(user2).createPost(post)
        post2 = create_dummy_instance(PostDTO)
        post2.group = None
        GroupManagement(user3).createPost(post2)

        fm.addFriend(user2)
        posts = fm.listPosts()

        assert isinstance(posts, list)
        assert len(posts) == 1
        assert isinstance(posts[0], PostDTO)

        fm.addFriend(user3)
        posts = fm.listPosts()

        assert isinstance(posts, list)
        assert len(posts) == 2
        assert isinstance(posts[0], PostDTO)
        assert isinstance(posts[1], PostDTO)
