from django.db import models


class UserMeta(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to="profiles/", null=True, blank=True)
    favorite_artist = models.CharField(max_length=255, null=True, blank=True)
    favorite_genre = models.CharField(max_length=100, null=True, blank=True)

    ### Es sind grade 2 verschiedene Wege von Permissions implementiert, wir müssen uns auf eine einigen. Am besten machen wir das wenn wir die Groups bearbeiten und schauen
    ### was dann am besten/einfachsten funktioniert.
    #
    # groups = models.ManyToManyField(
    #     Group,
    #     related_name="custom_user_set",
    #     blank=True,
    #     help_text="The groups this user belongs to.",
    #     verbose_name="groups",
    #     related_query_name="custom_user",
    # )

    # user_permissions = models.ManyToManyField(
    #     Permission,
    #     related_name="custom_user_set",
    #     blank=True,
    #     help_text="Specific permissions for this user.",
    #     verbose_name="user permissions",
    #     related_query_name="custom_user",
    # )


class Group(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    is_public = models.BooleanField(default=True)
    password = models.CharField(max_length=50, null=True, blank=True)
    max_posts_per_day = models.IntegerField(default=1)
    genre = models.CharField(max_length=50, null=True, blank=True)
    admin = models.ForeignKey(UserMeta, on_delete=models.CASCADE)
    profile_image = models.CharField(max_length=200, null=True, blank=True)
    post_permission = models.CharField(max_length=50)
    read_permission = models.CharField(max_length=50)


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
    posted_at = models.DateTimeField(auto_now_add=True)


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
