from rest_framework import serializers
from mainapp.models import UserMeta, Group, Membership, Music, Post, Comment, Vote


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = UserMeta
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
