from django.db import models
from django.utils import timezone


class UserMeta(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to="profiles/", null=True, blank=True)
    favorite_artist = models.CharField(max_length=255, null=True, blank=True)
    favorite_genre = models.CharField(max_length=100, null=True, blank=True)


class FriendsCombination(models.Model):
    id = models.AutoField(primary_key=True)
    baseUser = models.ForeignKey(
        UserMeta, on_delete=models.CASCADE, related_name="friendships_baseUser"
    )
    friend = models.ForeignKey(
        UserMeta, on_delete=models.CASCADE, related_name="friendship_friend"
    )

    class Meta:
        unique_together = ("baseUser", "friend")


class Group(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    is_public = models.BooleanField(default=True)
    password = models.CharField(max_length=50, null=True, blank=True)
    max_posts_per_day = models.IntegerField(default=1)
    post_permission = models.CharField(max_length=50, default="member")
    # profile_Image = models.ImageField(upload_to="group_images/", null=True, blank=True)
    genre = models.CharField(max_length=50, null=True, blank=True)
    admin = models.ForeignKey(UserMeta, on_delete=models.CASCADE)
    profile_image = models.CharField(max_length=200, null=True, blank=True)


class Membership(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserMeta, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("moderator", "Moderator"),
        ("member", "Member"),
        ("archive_viewer", "Archive Viewer"),
    ]
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default="member")

    class Meta:
        unique_together = ("user", "group")


class Music(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    album = models.CharField(max_length=255, null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)
    preview_url = models.URLField(null=True, blank=True)
    song_url = models.URLField(null=True, blank=True)


class Post(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserMeta, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    music = models.ForeignKey(Music, on_delete=models.CASCADE)
    posted_at = models.DateTimeField(default=timezone.now)


class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserMeta, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Vote(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserMeta, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    is_upvote = models.BooleanField()

    class Meta:
        unique_together = ("user", "post")
