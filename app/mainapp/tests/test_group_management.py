import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware

from mainapp.services.GroupManagement import GroupManagement
from mainapp.services.database import DatabaseManagement
from mainapp.objects.dtos import UserDTO, GroupDTO, MembershipDTO, PostDTO, MusicDTO
from mainapp.objects.dto_enums import DTOEnum, RoleEnum
from mainapp.objects.exceptions import DailyFavouriteDBObjectNotFound
from mainapp.tests.helpers import create_dummy_instance

@pytest.mark.django_db
class TestGroupManagement:

    @pytest.fixture
    def simUser(self):
        user = User.objects.create_user(username="dummy", password="pw")
        dto = UserDTO(user.id, user.username, None, None, None)
        DatabaseManagement(dto).get_or_create(dto, DTOEnum.USER)
        return dto
    
    @pytest.fixture
    def simGroup(self, simUser):
        group = create_dummy_instance(GroupDTO)
        group.id = 1
        group.admin = simUser
        DatabaseManagement(simUser).get_or_create(group, DTOEnum.GROUP)
        return group
    
    @pytest.fixture
    def simMembership(self, simUser, simGroup):
        membership = MembershipDTO(None, simUser, simGroup, RoleEnum.OWNER.value)
        DatabaseManagement(simUser).get_or_create(membership, DTOEnum.MEMBERSHIP)
        return membership
    
    @pytest.fixture
    def simRequest(self, simUser):
        request = RequestFactory().get("/")
        SessionMiddleware(get_response=lambda x: x).process_request(request)
        AuthenticationMiddleware(lambda r: r).process_request(request)
        request.session.save()
        request.user = User.objects.get(username=simUser.username)
        return request
    
    def testgetGroup(self, simRequest, simGroup):
        group_management = GroupManagement(simRequest.user)
        group = group_management.getGroup(simGroup.id)
        assert isinstance(group, GroupDTO)
        assert group.id == simGroup.id

    def testlistGroups(self, simRequest, simGroup):
        group_management = GroupManagement(simRequest.user)
        groups = group_management.listGroups()
        assert isinstance(groups, list)
        assert len(groups) > 0
        assert isinstance(groups[0], GroupDTO)

    def testlistGroupsWhereUserIsMember(self, simRequest, simMembership):
        group_management = GroupManagement(simRequest.user)
        groups = group_management.listGroupsWhereUserIsMember()
        assert isinstance(groups, list)
        assert len(groups) > 0
        assert isinstance(groups[0], GroupDTO)
        assert groups[0].id == simMembership.group.id

    def testcreateGroup(self, simRequest, simUser):
        group_management = GroupManagement(simRequest.user)
        new_group = create_dummy_instance(GroupDTO)
        new_group.admin = simUser
        group_management.createGroup(new_group)

        created_group = group_management.getGroup(new_group.id)
        assert isinstance(created_group, GroupDTO)
        assert created_group.admin.id == simUser.id

    def testupdateGroup(self, simRequest, simGroup):
        group_management = GroupManagement(simRequest.user)
        simGroup.name = "Updated Group Name"
        group_management.updateGroup(simGroup)

        updated_group = group_management.getGroup(simGroup.id)
        assert updated_group.name == "Updated Group Name"

    def testdeleteGroup(self, simRequest, simGroup):
        group_management = GroupManagement(simRequest.user)
        group_management.deleteGroup(simGroup)

        with pytest.raises(DailyFavouriteDBObjectNotFound):
            group_management.getGroup(simGroup.id)

    def testjoinGroup(self, simRequest, simGroup):
        group_management = GroupManagement(simRequest.user)
        membership = MembershipDTO(None, simRequest.user, simGroup, RoleEnum.MEMBER.value)
        group_management.createGroup(simGroup)

    def testleaveGroup(self, simRequest, simGroup):
        group_management = GroupManagement(simRequest.user)
        membership = MembershipDTO(None, simRequest.user, simGroup, RoleEnum.MEMBER.value)
        group_management.createGroup(simGroup)

        DatabaseManagement(simRequest.user).delete(membership, DTOEnum.MEMBERSHIP)

        with pytest.raises(DailyFavouriteDBObjectNotFound):
            group_management.getGroup(simGroup.id)

    def testgetMembers(self, simRequest, simGroup, simMembership):
        group_management = GroupManagement(simRequest.user)
        members = group_management.listGroupsWhereUserIsMember()

        assert isinstance(members, list)
        assert len(members) > 0
        assert isinstance(members[0], GroupDTO)
        assert members[0].id == simGroup.id

    def testuserIsMemberOfGroup(self, simRequest, simGroup, simMembership):
        group_management = GroupManagement(simRequest.user)
        is_member = group_management.userIsMemberOfGroup(simGroup)

        assert is_member is True

    def testremoveUserFromGroup(self, simRequest, simGroup, simMembership):
        group_management = GroupManagement(simRequest.user)
        group_management.deleteGroup(simGroup)

        with pytest.raises(DailyFavouriteDBObjectNotFound):
            group_management.getGroup(simGroup.id)

    def testcreatePost(self, simRequest, simGroup):
        group_management = GroupManagement(simRequest.user)
        post = create_dummy_instance(PostDTO)
        post.group = simGroup
        post.user = simRequest.user

        group_management.createPost(post)

        created_post = group_management.getPost(post.id)
        assert isinstance(created_post, PostDTO)
        assert created_post.group.id == simGroup.id
        assert created_post.user.id == simRequest.user.id
    
    def testdeletePost(self, simRequest, simGroup):
        group_management = GroupManagement(simRequest.user)
        post = create_dummy_instance(PostDTO)
        post.group = simGroup
        post.user = simRequest.user

        group_management.createPost(post)
        group_management.deletePost(post)

        with pytest.raises(DailyFavouriteDBObjectNotFound):
            group_management.getPost(post.id)

    def testcreatePrivateArchiveGroupIfNotExists(self, simRequest):
        group_management = GroupManagement(simRequest.user)
        group = create_dummy_instance(GroupDTO)
        group.is_public = False
        group.name = "Private Archive"
        group.description = "A private archive for personal posts."
        
        group_management.createGroup(group)

        created_group = group_management.getGroup(group.id)
        assert isinstance(created_group, GroupDTO)
        assert created_group.is_public is False
        assert created_group.name == "Private Archive"

    def testsyncPostToArchiveGroup(self, simRequest, simGroup):
        group_management = GroupManagement(simRequest.user)
        post = create_dummy_instance(PostDTO)
        post.group = simGroup
        post.user = simRequest.user

        group_management.createPost(post)
        group_management.syncPostToArchiveGroup(post)

        archive_group = group_management.getPrivateArchiveGroup()
        assert archive_group is not None
        assert isinstance(archive_group, GroupDTO)

        archived_posts = group_management.listPosts(archive_group)
        assert len(archived_posts) > 0
        assert archived_posts[0].id == post.id


