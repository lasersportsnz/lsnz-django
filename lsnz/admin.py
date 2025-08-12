from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


# Register your models here.
from .models import Grade, Player, Post, Site, Event, Team, Registration

admin.site.register(Grade)
admin.site.register(Player)
admin.site.register(Post)
admin.site.register(Site)
admin.site.register(Event)
admin.site.register(Team)
admin.site.register(Registration)