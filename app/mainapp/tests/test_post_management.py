import pytest

from django.contrib.auth.models import User
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware


from mainapp.services.userManagement import UserManagement
from mainapp.services.PostManagement import PostManagement
from mainapp.services.database import DatabaseManagement
from mainapp.objects.dtos import CommentDTO, PostDTO, GroupDTO, UserDTO
from mainapp.objects.dto_enums import DTOEnum
from mainapp.objects.exceptions import (
    DailyFavouriteAlreadyVotedForPost,
    DailyFavouriteDBObjectNotFound,
)
from mainapp.tests.helpers import TEST_DATE, create_dummy_instance

USERNAME = "testuser"
PASSWORD = "testpassword"


@pytest.mark.django_db
class TestPostManagement:
    """
    Testklasse für die PostManagement
    """

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
    def simPost1(self):
        post_dto = create_dummy_instance(PostDTO)
        post_dto.id = 1
        return post_dto

    @pytest.fixture
    def simPost2(self):
        post_dto = create_dummy_instance(PostDTO)
        post_dto.id = 2
        return post_dto

    # Tests
    def test_create_get_and_delete_post(self, simRequest, simPost1):
        user = UserManagement(simRequest).getCurrentUser()
        assert user is not None

        pm = PostManagement(user)
        pm.createPost(simPost1)

        post = pm.getPost(id=simPost1.id)

        assert post is not None
        assert type(post) is PostDTO

        pm.deletePost(post)

        with pytest.raises(DailyFavouriteDBObjectNotFound):
            pm.getPost(id=simPost1.id)

    def test_list_group_posts(self, simRequest, simPost1, simPost2):
        user = UserManagement(simRequest).getCurrentUser()
        assert user is not None

        pm = PostManagement(user)

        group = GroupDTO(
            id=1,
            name="TestGroup",
            created_at=TEST_DATE,
            description="TestDescription",
            is_public=True,
            max_posts_per_day=1,
            read_permission="all",
            post_permission="all",
            profile_image=None,
            genre=None,
            admin=user,
        )
        simPost1.group = group
        simPost2.group = group
        pm.createPost(simPost1)
        pm.createPost(simPost2)

        posts = pm.listPosts(group)

        assert posts is not None
        assert type(posts) is list
        assert len(posts) == 2
        assert type(posts[0]) is PostDTO
        assert type(posts[1]) is PostDTO

    def test_list_users_posts(self, simRequest, simPost1, simPost2):
        user = UserManagement(simRequest).getCurrentUser()
        assert user is not None

        pm = PostManagement(user)
        pm.createPost(simPost1)

        user2 = user
        user2.id = 2
        simPost2.user = user2
        pm.createPost(simPost2)

        posts = pm.listPosts(users=[user.id, user2.id])

        assert posts is not None
        assert type(posts) is list
        assert len(posts) == 2
        assert type(posts[0]) is PostDTO
        assert type(posts[1]) is PostDTO

    def test_upvote_post(self, simRequest, simPost1):
        user = UserManagement(simRequest).getCurrentUser()
        assert user is not None

        pm = PostManagement(user)
        pm.createPost(simPost1)
        votes = pm.get_up_and_down_votes(simPost1)
        assert votes == (0, 0)

        pm.upvotePost(simPost1)
        votes = pm.get_up_and_down_votes(simPost1)
        assert votes == (1, 0)

        with pytest.raises(DailyFavouriteAlreadyVotedForPost):
            pm.upvotePost(simPost1)

    def test_downvote_post(self, simRequest, simPost1):
        user = UserManagement(simRequest).getCurrentUser()
        assert user is not None

        pm = PostManagement(user)
        pm.createPost(simPost1)
        votes = pm.get_up_and_down_votes(simPost1)
        assert votes == (0, 0)

        pm.downVotePost(simPost1)
        votes = pm.get_up_and_down_votes(simPost1)
        assert votes == (0, 1)

        with pytest.raises(DailyFavouriteAlreadyVotedForPost):
            pm.downVotePost(simPost1)

    def test_comment_post(self, simRequest, simPost1):
        user = UserManagement(simRequest).getCurrentUser()
        assert user is not None

        pm = PostManagement(user)
        pm.createPost(simPost1)
        comments = pm.getCommentsForPost(simPost1)
        assert comments is not None
        assert len(comments) == 0

        pm.commentPost(simPost1, "Test Kommentar 1")
        comments = pm.getCommentsForPost(simPost1)
        assert comments is not None
        assert len(comments) == 1
        assert type(comments[0]) is CommentDTO
        assert comments[0].user == user.id
        assert comments[0].post == simPost1.id
        assert comments[0].content == "Test Kommentar 1"

        pm.commentPost(simPost1, "Test Kommentar 2")
        comments = pm.getCommentsForPost(simPost1)
        assert comments is not None
        assert len(comments) == 2
        assert type(comments[1]) is CommentDTO
        assert comments[1].user == user.id
        assert comments[1].post == simPost1.id
        assert comments[1].content == "Test Kommentar 2"

    def test_convert_to_json(self, simRequest, simPost1, simPost2):
        user = UserManagement(simRequest).getCurrentUser()
        assert user is not None

        simPost1.user = user
        simPost2.user = user

        pm = PostManagement(user)
        pm.createPost(simPost1)
        pm.upvotePost(simPost1)
        pm.commentPost(simPost1, "TestPost1")

        pm.createPost(simPost2)
        pm.downVotePost(simPost2)
        pm.commentPost(simPost2, "TestPost2")

        jsons = pm.convert_to_json(pm.listPosts(users=[user.id]))

        assert jsons is not None
        assert type(jsons) is list
        assert len(jsons) == 2

        for json in jsons:
            assert type(json) is dict
            assert [
                "id",
                "user",
                "group",
                "music",
                "posted_at",
                "comments",
                "votes",
            ] == list(json.keys())
