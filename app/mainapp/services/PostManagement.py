from typing import List, Tuple
from datetime import datetime

from mainapp.objects.exceptions import (
    DailyFavouriteAlreadyVotedForPost,
    DailyFavouriteDBObjectCouldNotBeCreated,
    DailyFavouriteDBObjectNotFound,
    DailyFavouriteDBWrongObjectType,
    DailyFavouriteMinimumRequiredParameter,
)
from mainapp.objects.dtos import UserDTO, PostDTO, GroupDTO, CommentDTO, VoteDTO
from mainapp.objects.enums import DTOEnum
from mainapp.services.database import DatabaseManagement


class PostManagement:
    user: UserDTO

    def __init__(self, user: UserDTO) -> None:
        self.user = user

    def getPost(self, id: int) -> PostDTO:
        obj = DatabaseManagement(self.user).get(id, DTOEnum.POST)

        if type(obj) is PostDTO:
            return obj
        else:
            raise DailyFavouriteDBWrongObjectType(PostDTO, type(obj))

    def listPosts(
        self, group: GroupDTO | None = None, users: List[int] | None = None
    ) -> List[PostDTO]:
        """
        Expextes GroupDTO of group or IDs of users.
        """
        if group is not None:
            return DatabaseManagement(self.user).list(
                group.id, DTOEnum.POST, "group_id"
            )
        elif users is not None:
            dtos = []
            for user in users:
                dtos.extend(
                    DatabaseManagement(self.user).list(user, DTOEnum.POST, "user_id")
                )
            return dtos

        raise DailyFavouriteMinimumRequiredParameter(
            "PostManagement.ListPosts", "Missing group or friends."
        )

    def createPost(self, post: PostDTO) -> None:
        DatabaseManagement(self.user).get_or_create(post, DTOEnum.POST)

    def deletePost(self, post: PostDTO) -> None:
        DatabaseManagement(self.user).delete(post, DTOEnum.POST)

    def upvotePost(self, post: PostDTO) -> None:
        vote_dto = VoteDTO(None, self.user, post, True)
        try:
            DatabaseManagement(self.user).get_or_create(vote_dto, DTOEnum.VOTE)
        except DailyFavouriteDBObjectCouldNotBeCreated:
            raise DailyFavouriteAlreadyVotedForPost()

    def downVotePost(self, post: PostDTO) -> None:
        vote_dto = VoteDTO(None, self.user, post, False)
        try:
            DatabaseManagement(self.user).get_or_create(vote_dto, DTOEnum.VOTE)
        except DailyFavouriteDBObjectCouldNotBeCreated:
            raise DailyFavouriteAlreadyVotedForPost()

    def get_up_and_down_votes(self, post: PostDTO) -> Tuple[int, int]:
        try:
            votes = DatabaseManagement(self.user).list(post.id, DTOEnum.VOTE, "post_id")
        except DailyFavouriteDBObjectNotFound:
            return (0, 0)

        upvotes = 0
        downvotes = 0

        for vote in votes:
            if type(vote) is not VoteDTO:
                raise DailyFavouriteDBWrongObjectType(VoteDTO, type(vote))

            if vote.is_upvote:
                upvotes += 1
            else:
                downvotes += 1

        return (upvotes, downvotes)

    def commentPost(self, post: PostDTO, comment: str) -> None:
        comment_dto = CommentDTO(None, self.user, post, comment, datetime.now())
        DatabaseManagement(self.user).get_or_create(comment_dto, DTOEnum.COMMENT)

    def getCommentsForPost(self, post: PostDTO) -> List[CommentDTO]:
        try:
            return DatabaseManagement(self.user).list(
                post.id, DTOEnum.COMMENT, "post_id"
            )
        except DailyFavouriteDBObjectNotFound:
            return []

    def convert_to_json(self, posts: PostDTO | List[PostDTO]) -> List:
        if type(posts) is PostDTO:
            posts = [posts]

        jsons = []
        dbm = DatabaseManagement(self.user)

        for post in posts:
            comments = self.getCommentsForPost(post)
            votes = self.get_up_and_down_votes(post)
            votes_diff = votes[0] - votes[1]
            user = dbm.get(post.user, DTOEnum.USER)
            group = dbm.get(post.group, DTOEnum.GROUP)
            music = dbm.get(post.music, DTOEnum.MUSIC)

            post_json = {
                "id": post.id,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "profile_picture": user.profile_picture,
                    "favorite_artist": user.favorite_artist,
                    "favorite_genre": user.favorite_genre,
                },
                "group": {
                    "id": group.id,
                    "name": group.name,
                    "created_at": group.created_at,
                    "description": group.description,
                    "is_public": group.is_public,
                    "max_posts_per_day": group.max_posts_per_day,
                    "post_permission": group.post_permission,
                    "read_permission": group.read_permission,
                },
                "music": {
                    "id": music.id,
                    "name": music.name,
                    "artist": music.artist,
                    "album": music.album,
                    "image_url": music.image_url,
                    "preview_url": music.preview_url,
                    "song_url": music.song_url,
                },
                "posted_at": post.posted_at,
                "comments": [
                    {
                        "id": comment.id,
                        "user": (
                            lambda u: {
                                "id": u.id,
                                "username": u.username,
                                "profile_picture": u.profile_picture,
                                "favorite_artist": u.favorite_artist,
                                "favorite_genre": u.favorite_genre,
                            }
                        )(dbm.get(comment.user, DTOEnum.USER)),
                        "content": comment.content,
                        "created_at": comment.created_at,
                    }
                    for comment in comments
                ],
                "votes": {
                    "upvotes": votes[0],
                    "downvotes": votes[1],
                    "differenz": votes_diff,
                },
            }

            jsons.append(post_json)

        return jsons
