from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserMeta(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    profile_picture = models.ImageField(upload_to="profiles/", null=True, blank=True)
    favorite_artist = models.CharField(max_length=255, null=True, blank=True)
    favorite_genre = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.username

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
    GENRE_CHOICES = [
        ('Pop', 'Pop'),
        ('Rock', 'Rock'),
        ('Hip-Hop', 'Hip-Hop'),
        ('Electronic', 'Electronic'),
        ('Jazz', 'Jazz'),
        ('Classical', 'Classical'),
        ('Indie', 'Indie'),
        ('Metal', 'Metal'),
        ('Folk', 'Folk'),
        ('Schlager', 'Schlager'),
        ('Andere', 'Andere'),
        ('Gemischt', 'Gemischt'),
    ]

    PERMISSION_CHOICES = [
        ('all', 'Alle Mitglieder'),
        ('moderators', 'Nur Moderatoren'),
        ('owner', 'Nur Besitzer'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    is_public = models.BooleanField(default=True)
    profile_image = models.ImageField(upload_to='group_images/', null=True, blank=True)
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, null=True, blank=True)
    members = models.ManyToManyField(UserMeta, related_name='user_groups', blank=True)
    owner = models.ForeignKey(
        UserMeta,
        on_delete=models.SET_NULL,
        related_name='owned_groups',
        null=True,
        blank=True
    )

    max_posts_per_day = models.IntegerField(default=1)
    post_permission = models.CharField(max_length=50, default='all')
    read_permission = models.CharField(max_length=50, default='all')

    post_permission = models.CharField(
        max_length=20,
        choices=PERMISSION_CHOICES,
        default='all'
    )
    read_permission = models.CharField(
        max_length=20,
        choices=PERMISSION_CHOICES,
        default='all'
    )

    def __str__(self):
        return self.name


class Membership(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserMeta, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

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

@receiver(post_save, sender=User)
def create_usermeta(sender, instance, created, **kwargs):
    if created:
        UserMeta.objects.create(user=instance)

