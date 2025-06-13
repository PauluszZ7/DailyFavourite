from django.contrib import admin
from mainapp.models import Membership, UserMeta, Group, Post, Vote, Music, Comment

# Register your models here.
admin.site.register(Membership)
admin.site.register(UserMeta)
admin.site.register(Group)
admin.site.register(Post)
admin.site.register(Vote)
admin.site.register(Music)
admin.site.register(Comment)
