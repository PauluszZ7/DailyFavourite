from enum import Enum
from mainapp.models import UserMeta, Group, Music, Post, Comment, Vote
from mainapp.objects.serializers import (
    UserSerializer,
    GroupSerializer,
    MusicSerializer,
    PostSerializer,
    CommentSerializer,
    VoteSerializer,
)
from mainapp.objects.dtos import (
    ModelDTO,
    UserDTO,
    GroupDTO,
    MusicDTO,
    CommentDTO,
    PostDTO,
    VoteDTO,
)


class DTOEnum(Enum):
    USER = "User"
    GROUP = "Group"
    MUSIC = "Music"
    COMMENT = "Comment"
    POST = "Post"
    VOTE = "Vote"

    def getModel(self):
        """
        Returns Model of DTO Type
        """
        if self.value == "User":
            return UserMeta
        elif self.value == "Group":
            return Group
        elif self.value == "Music":
            return Music
        elif self.value == "Comment":
            return Comment
        elif self.value == "Post":
            return Post
        elif self.value == "Vote":
            return Vote

    def getSerializer(self):
        """
        Returns Serializer of DTO Type
        """

        if self.value == "User":
            return UserSerializer
        elif self.value == "Group":
            return GroupSerializer
        elif self.value == "Music":
            return MusicSerializer
        elif self.value == "Comment":
            return CommentSerializer
        elif self.value == "Post":
            return PostSerializer
        elif self.value == "Vote":
            return VoteSerializer

    def getDTO(self):
        """
        Returns DTO of DTO Type
        """
        if self.value == "User":
            return UserDTO
        elif self.value == "Group":
            return GroupDTO
        elif self.value == "Music":
            return MusicDTO
        elif self.value == "Comment":
            return CommentDTO
        elif self.value == "Post":
            return PostDTO
        elif self.value == "Vote":
            return VoteDTO

    @classmethod
    def fromDTO(cls, dto: ModelDTO):
        if type(dto) is UserDTO:
            return DTOEnum.USER
        elif type(dto) is GroupDTO:
            return DTOEnum.GROUP
        elif type(dto) is MusicDTO:
            return DTOEnum.MUSIC
        elif type(dto) is CommentDTO:
            return DTOEnum.COMMENT
        elif type(dto) is PostDTO:
            return DTOEnum.POST
        elif type(dto) is VoteDTO:
            return DTOEnum.VOTE
