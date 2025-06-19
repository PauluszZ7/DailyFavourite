import pytest

from django.contrib.auth.models import User
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware

from mainapp.services.userManagement import UserManagement
from mainapp.services.friendsManagement import FriendsManagement
from mainapp.services.database import DatabaseManagement
from mainapp.objects.dtos import UserDTO
from mainapp.objects.enums import DTOEnum

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
        assert friends_list[0] is friends_user

        fm.removeFriend(friends_user)
        friends_list = fm.getFriends() 

        assert isinstance(friends_list, list)
        assert len(friends_list) == 0

