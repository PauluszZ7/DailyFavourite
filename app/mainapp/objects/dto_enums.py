from enum import Enum
from typing import List
from dataclasses import asdict
from mainapp.models import (
    Membership,
    UserMeta,
    Group,
    Music,
    Post,
    Comment,
    Vote,
    FriendsCombination,
)
from mainapp.objects.serializers import (
    UserSerializer,
    GroupSerializer,
    MusicSerializer,
    PostSerializer,
    CommentSerializer,
    VoteSerializer,
    MembershipSerializer,
    FriendsCombinationSerializer,
)
from mainapp.objects.dtos import (
    ModelDTO,
    UserDTO,
    GroupDTO,
    MusicDTO,
    CommentDTO,
    PostDTO,
    VoteDTO,
    MembershipDTO,
    FriendsCombinationDTO,
)


class DTOEnum(Enum):
    USER = "User"
    GROUP = "Group"
    MUSIC = "Music"
    COMMENT = "Comment"
    POST = "Post"
    VOTE = "Vote"
    MEMBERSHIP = "Membership"
    FRIENDSCOMBINTAION = "FriendsCombination"

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
        elif self.value == "Membership":
            return Membership
        elif self.value == "FriendsCombination":
            return FriendsCombination

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
        elif self.value == "Membership":
            return MembershipSerializer
        elif self.value == "FriendsCombination":
            return FriendsCombinationSerializer

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
        elif self.value == "Membership":
            return MembershipDTO
        elif self.value == "FriendsCombination":
            return FriendsCombinationDTO
    
    def convertToJSON(self, data: List[ModelDTO]):
        if len(data) > 0:
            return [asdict(obj) for obj in data]
        else:
            return []

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
        elif type(dto) is MembershipDTO:
            return DTOEnum.MEMBERSHIP
        elif type(dto) is FriendsCombinationDTO:
            return DTOEnum.FRIENDSCOMBINTAION
