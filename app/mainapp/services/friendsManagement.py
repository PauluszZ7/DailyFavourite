from typing import List
from mainapp.services.database import DatabaseManagement
from mainapp.objects.dtos import UserDTO, FriendsCombinationDTO
from mainapp.objects.enums import DTOEnum
from mainapp.objects.exceptions import DailyFavouriteDBObjectCouldNotBeCreated, DailyFavouriteAlredyFriends, DailyFavouriteDBObjectNotFound


class FriendsManagement:
    user: UserDTO

    def __init__(self, user:UserDTO) -> None:
        self.user = user
    
    def addFriend(self, friend: UserDTO):
        friendDTO = FriendsCombinationDTO(None, self.user, friend) 
        try:
            DatabaseManagement(self.user).get_or_create(friendDTO, DTOEnum.Friend)
        except DailyFavouriteDBObjectCouldNotBeCreated:
            raise DailyFavouriteAlredyFriends()

    def removeFriend(self, friend: UserDTO):
        friendDTO = FriendsCombinationDTO(None, self.user, friend)
        friendsList = self.getFriends()

        for f in friendsList:
            if f.friend.id == friend.id:
                friendDTO.id = f.id

        if friendDTO.id is None:
            raise DailyFavouriteDBObjectNotFound(DTOEnum.FRIEND, friend.id)

        DatabaseManagement(self.user).delete(friendDTO, DTOEnum.FRIEND)

    def listPosts(self) -> List[UserDTO]:
        pass

    def getFriends(self) -> List[FriendsCombinationDTO]:
        try:
            return DatabaseManagement(self.user).list(self.user.id, DTOEnum.FRIEND, "baseUser_id")
        except DailyFavouriteDBObjectNotFound:
            return []

    def searchUsers(self, name:str) -> List[UserDTO]:
        try:
            user_list = DatabaseManagement(self.user).list(name, DTOEnum.USER, "username_icontains")
        except DailyFavouriteDBObjectNotFound:
            return []
        
        for user in user_list:
            if self.user.username == user.username:
                user_list.remove(user)
                break

        return user_list


