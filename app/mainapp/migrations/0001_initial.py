# Generated by Django 5.2 on 2025-06-04 17:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Group",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("is_public", models.BooleanField(default=True)),
                ("max_posts_per_day", models.IntegerField(default=1)),
                ("post_permission", models.CharField(max_length=50)),
                ("read_permission", models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name="Music",
            fields=[
                (
                    "id",
                    models.CharField(max_length=100, primary_key=True, serialize=False),
                ),
                ("name", models.CharField(max_length=255)),
                ("artist", models.CharField(max_length=255)),
                ("album", models.CharField(blank=True, max_length=255, null=True)),
                ("image_url", models.URLField(blank=True, null=True)),
                ("preview_url", models.URLField(blank=True, null=True)),
                ("song_url", models.URLField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="UserMeta",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("username", models.CharField(max_length=100)),
                (
                    "profile_picture",
                    models.ImageField(blank=True, null=True, upload_to="profiles/"),
                ),
                (
                    "favorite_artist",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "favorite_genre",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Post",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("posted_at", models.DateTimeField(auto_now_add=True)),
                (
                    "group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="mainapp.group"
                    ),
                ),
                (
                    "music",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="mainapp.music"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mainapp.usermeta",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Comment",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("content", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="mainapp.post"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mainapp.usermeta",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Membership",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="mainapp.group"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mainapp.usermeta",
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "group")},
            },
        ),
        migrations.CreateModel(
            name="Vote",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("is_upvote", models.BooleanField()),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="mainapp.post"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mainapp.usermeta",
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "post")},
            },
        ),
    ]