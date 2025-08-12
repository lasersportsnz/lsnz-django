import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

from .managers import CustomUserManager

# Create your models here.

AUTH_USER_MODEL = "lsnz.Player"

class Grade(models.Model):
    letter = models.CharField(max_length=4)
    points = models.IntegerField(default=0)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.letter

class Player(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    alias = models.CharField(max_length=20, unique=True)
    grade = models.ForeignKey(Grade, on_delete=models.PROTECT, db_index=True, blank=True, null=True)
    profile_picture = models.CharField(max_length=200, blank=True, null=True)
    playing_since = models.DateTimeField(_("playing since"), db_index=True, auto_now_add=True)
    bio = models.CharField(max_length=140, blank=True, null=True)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "alias"]

    objects = CustomUserManager()

    def __str__(self):
        return self.alias
    
class Post(models.Model):
    title = models.CharField(max_length=50)
    summary = models.CharField(max_length=200)
    body = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    created_at = models.DateTimeField(db_index=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_index=True, auto_now=True)
    author = models.ForeignKey(Player, on_delete=models.PROTECT)

    def from_dict(self, data):
        for field in ['title', 'body']:
            if field in data:
                setattr(self, field, data[field])
        if 'created_at' in data:
            self.created_at = datetime.fromisoformat(data['created_at'])

    def __str__(self):
        return self.title
 
class Site(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    system = models.CharField(max_length=50)

    def from_dict(self, data):
        for field in ['name', 'country', 'address', 'system']:
            if field in data:
                setattr(self, field, data[field])

    def __str__(self):
        return f'<Site {self.name} in {self.country}>'

class Event(models.Model):
    name =  models.CharField(max_length=200)
    site = models.ForeignKey(Site, on_delete=models.PROTECT)
    date = models.DateTimeField("Event date", db_index=True)
    points_cap = models.IntegerField(default=30)
    format = models.CharField(max_length=50)

    def from_dict(self, data):
        for field in ['name', 'site_id', 'date', 'points_cap', 'format']:
            if field in data:
                setattr(self, field, data[field])

    def __str__(self):
        return f'<Event {self.name} at {self.site_id}>'

class Team(models.Model):
    name = models.CharField(max_length=50)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def from_dict(self, data):
        for field in ['name', 'event_id']:
            if field in data:
                setattr(self, field, data[field])
                
    def __str__(self):
        return f'<Team {self.name} for {self.event}>'

class Registration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.PROTECT, db_index=True)
    paid = models.BooleanField(default=False)

    def from_dict(self, data):
        for field in ['event_id', 'player_id', 'team_id', 'paid']:
            if field in data:
                setattr(self, field, data[field])

    def __str__(self):
        return f'<Registration for {self.event} by {self.player}>'