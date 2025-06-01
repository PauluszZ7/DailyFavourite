from django.db import models


class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    profile_picture = models.ImageField(upload_to="profiles/", null=True, blank=True)
    favorite_artist = models.CharField(max_length=255, null=True, blank=True)
    favorite_genre = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.username


class Group(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    is_public = models.BooleanField(default=True)
    max_posts_per_day = models.IntegerField(null=True, blank=True)
    post_permission = models.CharField(
        max_length=50, default="all"
    )  # all / members / admin
    read_permission = models.CharField(max_length=50, default="all")

    members = models.ManyToManyField(User, through="Membership")

    def __str__(self):
        return self.name


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "group")

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"


class Music(models.Model):
    name = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    album = models.CharField(max_length=255, null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)
    preview_url = models.URLField(null=True, blank=True)
    song_url = models.URLField()

    def __str__(self):
        return f"{self.name} – {self.artist}"


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    music = models.ForeignKey(Music, on_delete=models.CASCADE)
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.user.username} – {self.music.name}"


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    is_upvote = models.BooleanField()

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{'Upvote' if self.is_upvote else 'Downvote'} by {self.user.username}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.music.name}"
