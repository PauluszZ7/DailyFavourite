from django.contrib.auth.models import User
from django.db import models

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

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='group_images/', blank=True, null=True)
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES)
    is_public = models.BooleanField(default=True)

    members = models.ManyToManyField(User, related_name='user_groups')

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_groups', null=True, blank=True)

    def __str__(self):
        return self.name



