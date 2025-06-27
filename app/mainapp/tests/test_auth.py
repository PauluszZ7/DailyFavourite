import pytest

from django.contrib.auth.models import User
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware

from mainapp.objects.dto_enums import DTOEnum
from mainapp.services.database import DatabaseManagement
from mainapp.services.userManagement import UserManagement
from mainapp.objects.exceptions import DailyFavouriteNoUserFound
from mainapp.objects.dtos import UserDTO


USERNAME = "testuser"
PASSWORD = "testpassword"


@pytest.mark.django_db
class TestAuthentication:
    """
    Testklasse für die Authentication (UserManagement)
    """

    # Fixtures
    @pytest.fixture
    def simRequest(self):
        request = RequestFactory().get("/")
        SessionMiddleware(get_response=lambda x: x).process_request(request)
        AuthenticationMiddleware(lambda r: r).process_request(request)
        request.session.save()
        return request

    @pytest.fixture
    def simUser(self):
        user = User.objects.create_user(username=USERNAME, password=PASSWORD)
        dto = UserDTO(user.id, user.username, None, None, None)
        DatabaseManagement(dto).get_or_create(dto, DTOEnum.USER)
        return user

    # Tests
    def test_register(self, simRequest):
        dto = UserDTO(None, "user1", None, None, None)
        UserManagement(simRequest).register("user1", "password1", dto)
        user = User.objects.get(username="user1")
        user_dto = DatabaseManagement(dto).get(user.id, DTOEnum.USER)

        assert user is not None
        assert user.id is not None

        assert type(user_dto) is UserDTO
        assert user.id == user_dto.id
        assert user.username == user_dto.username

    def test_login(self, simRequest, simUser):
        UserManagement(simRequest).login(USERNAME, PASSWORD)
        assert simRequest.user.is_authenticated

    def test_get_user(self, simRequest, simUser):
        UserManagement(simRequest).login(USERNAME, PASSWORD)
        assert simRequest.user.is_authenticated

        user = UserManagement(simRequest).getCurrentUser()
        assert user is not None
        assert type(user) is UserDTO

    @pytest.mark.parametrize(
        "username, password",
        [
            (USERNAME, "wrongpassword"),
            ("wronguser", PASSWORD),
        ],
    )
    def test_login_fail(self, simRequest, simUser, username, password):
        with pytest.raises(DailyFavouriteNoUserFound):
            UserManagement(simRequest).login(username, password)

    def test_logout(self, simRequest, simUser):
        UserManagement(simRequest).login(USERNAME, PASSWORD)
        assert simRequest.user.is_authenticated

        UserManagement(simRequest).logout()
        assert not simRequest.user.is_authenticated

    @pytest.mark.parametrize("isLoggedIn", [(True), (False)])
    def test_check_is_logged_in(self, simRequest, simUser, isLoggedIn):
        if isLoggedIn:
            UserManagement(simRequest).login(USERNAME, PASSWORD)
            assert simRequest.user.is_authenticated

        assert UserManagement(simRequest).checkIsLoggedIn() == isLoggedIn

    def test_change_password(self, simRequest, simUser):
        UserManagement(simRequest).changeUserPassword(USERNAME, PASSWORD, "newpassword")
        simUser = User.objects.get(username=USERNAME)
        assert simUser.check_password("newpassword")

    def test_delete_password(self, simRequest, simUser):
        UserManagement(simRequest).login(USERNAME, PASSWORD)
        assert simRequest.user.is_authenticated

        UserManagement(simRequest).deleteUser(PASSWORD)
        assert not User.objects.filter(username=USERNAME).exists()
