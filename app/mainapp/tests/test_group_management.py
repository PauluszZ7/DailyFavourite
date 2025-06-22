# import pytest
# from datetime import datetime
# from unittest.mock import patch, MagicMock
# from mainapp.services.GroupManagement import GroupManagement
# from mainapp.objects.dtos import UserDTO, GroupDTO, PostDTO, MusicDTO, MembershipDTO
# from mainapp.objects.enums import RoleEnum, DTOEnum
# from mainapp.objects.exceptions import DailyFavouriteDBObjectNotFound

# # 🔧 Dummy Benutzer
# @pytest.fixture
# def dummy_user():
#     return UserDTO(
#         id=1,
#         username="testuser",
#         profile_picture=None,
#         favorite_artist=None,
#         favorite_genre=None
#     )

# # 🔧 Dummy Gruppe
# @pytest.fixture
# def dummy_group(dummy_user):
#     return GroupDTO(
#         id=123,
#         name="Testgruppe",
#         created_at=datetime.now(),
#         description="Testbeschreibung",
#         profile_image=None,
#         genre="pop",
#         is_public=True,
#         max_posts_per_day=10,
#         post_permission="admin",
#         read_permission="all",
#         admin=dummy_user
#     )

# # 🔧 Dummy Musik
# @pytest.fixture
# def dummy_music():
#     return MusicDTO(
#         id="track-123",
#         name="Test Song",
#         artist="Test Artist",
#         album="Test Album",
#         image_url=None,
#         preview_url=None,
#         song_url=None,
#     )

# # ✅ Test: Gruppe wird erstellt + Mitglied mit Rolle Owner
# @patch("mainapp.services.GroupManagement.DatabaseManagement")
# def test_create_group(mock_db, dummy_user, dummy_group):
#     gm = GroupManagement(dummy_user)

#     gm.createGroup(dummy_group)

#     mock_db.return_value.get_or_create.assert_any_call(dummy_group, DTOEnum.GROUP)
#     assert mock_db.return_value.get_or_create.call_count >= 2

# # ✅ Test: Archivgruppe wird erstellt (nicht doppelt)
# @patch("mainapp.services.GroupManagement.DatabaseManagement")
# def test_create_private_archive_group(mock_db, dummy_user):
#     gm = GroupManagement(dummy_user)

#     mock_db.return_value.list.side_effect = DailyFavouriteDBObjectNotFound(DTOEnum.GROUP, 0)

#     gm.createPrivateArchiveGroupIfNotExists()

#     assert mock_db.return_value.get_or_create.call_count >= 2
#     args, kwargs = mock_db.return_value.get_or_create.call_args_list[0]
#     assert args[1] == DTOEnum.GROUP
#     assert isinstance(args[0], GroupDTO)

# # ✅ Test: Nutzer wird Mitglied
# @patch("mainapp.services.GroupManagement.DatabaseManagement")
# def test_join_group(mock_db, dummy_user, dummy_group):
#     gm = GroupManagement(dummy_user)

#     mock_db.return_value.list.side_effect = DailyFavouriteDBObjectNotFound(DTOEnum.MEMBERSHIP, 0)

#     gm.joinGroup(dummy_group)

#     assert mock_db.return_value.get_or_create.call_count == 1
#     args, kwargs = mock_db.return_value.get_or_create.call_args
#     assert isinstance(args[0], MembershipDTO)
#     assert args[0].role == RoleEnum.MEMBER.value

# # ✅ Test: Sync zu Archivgruppe erstellt neuen Post
# @patch("mainapp.services.GroupManagement.PostManagement")
# @patch("mainapp.services.GroupManagement.DatabaseManagement")
# def test_sync_post_to_archive(mock_db, mock_pm, dummy_user, dummy_music, dummy_group):
#     gm = GroupManagement(dummy_user)

#     dummy_post = PostDTO(
#         id=None,
#         user=dummy_user,
#         group=dummy_group,
#         music=dummy_music,
#         posted_at=datetime.now(),
#     )

#     archive_group = dummy_group
#     archive_group.is_public = False
#     archive_group.name = f"{dummy_user.username}-archive-{dummy_user.id}"
#     archive_group.admin = dummy_user

#     mock_db.return_value.list.return_value = [archive_group]

#     gm.syncPostToArchiveGroup(dummy_post)

#     assert mock_pm.return_value.createPost.call_count == 1

# # ✅ Test: userIsMemberOfGroup = True
# @patch("mainapp.services.GroupManagement.DatabaseManagement")
# def test_user_is_member_true(mock_db, dummy_user, dummy_group):
#     gm = GroupManagement(dummy_user)

#     membership = MembershipDTO(None, dummy_user, dummy_group, RoleEnum.MEMBER.value)
#     mock_db.return_value.list.return_value = [membership]

#     assert gm.userIsMemberOfGroup(dummy_group) is True

# # ✅ Test: userIsMemberOfGroup = False
# @patch("mainapp.services.GroupManagement.DatabaseManagement")
# def test_user_is_member_false(mock_db, dummy_user, dummy_group):
#     gm = GroupManagement(dummy_user)

#     mock_db.return_value.list.side_effect = DailyFavouriteDBObjectNotFound(DTOEnum.MEMBERSHIP, 0)

#     assert gm.userIsMemberOfGroup(dummy_group) is False
