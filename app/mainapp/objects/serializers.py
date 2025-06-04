from rest_framework import serializers
from mainapp.models import User, Group, Membership, Music, Post, Comment, Vote

###### Beispiel verwendung
# from dataclasses import dataclass
# from dataclasses_json import dataclass_json
# from rest_framework import serializers

# @dataclass_json
# @dataclass
# class UserDTO:
#     id: int
#     username: str
#     profile_picture: str
#     favorite_artist: str
#     favorite_genre: str

# # Serialisierung
# user_instance = User.objects.get(id=1)
# user_serializer = UserSerializer(user_instance)
# json_data = user_serializer.data
# user_dto = UserDTO.from_json(json.dumps(json_data))

# # Deserialisierung
# json_input = '{"id": 2, "username": "user2", ...}'
# user_dto = UserDTO.from_json(json_input)
# # Mapping back zu Model oder weiteres Handling
########

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "profile_picture",
            "favorite_artist",
            "favorite_genre",
        ]


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = [
            "id",
            "name",
            "created_at",
            "description",
            "is_public",
            "max_posts_per_day",
            "post_permission",
            "read_permission",
        ]


class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ["id", "user", "group"]


class MusicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Music
        fields = [
            "id",
            "spotify_id",
            "name",
            "artist",
            "album",
            "image_url",
            "preview_url",
            "song_url",
        ]


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "user", "group", "music", "posted_at"]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "user", "post", "content", "created_at"]


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ["id", "user", "post", "is_upvote"]


class ImportTrackSerializer(serializers.Serializer):
    spotify_track_id = serializers.CharField(max_length=100)
