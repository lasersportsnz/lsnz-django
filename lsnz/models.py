from datetime import timedelta
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

from .managers import CustomUserManager

AUTH_USER_MODEL = "lsnz.Player"

COUNTRIES = [
    ('US', 'United States'),
    ('AU', 'Australia'),
    ('NZ', 'New Zealand'),
    ('DE', 'Germany'),
    ('FR', 'France'),
    ('FI', 'Finland'),
    ('SE', 'Sweden'),
    ('Other', 'Other')
]

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
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    playing_since = models.DateTimeField(_("playing since"), db_index=True, auto_now_add=True)
    home_site = models.ForeignKey('Site', on_delete=models.PROTECT, null=True, blank=True)
    bio = models.TextField()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "alias"]

    objects = CustomUserManager()

    class Meta(AbstractUser.Meta):
        verbose_name = "Player"
        verbose_name_plural = "Players"

    def __str__(self):
        return self.alias

class Post(models.Model):
    title = models.CharField(max_length=50)
    summary = models.CharField(max_length=200)
    body = models.TextField()
    image = models.ImageField(upload_to='post_images/')
    created_at = models.DateTimeField(db_index=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_index=True, auto_now=True)
    author = models.ForeignKey(Player, on_delete=models.PROTECT)

    def __str__(self):
        return self.title

class System(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='system_images/')
    description = models.TextField()

    def __str__(self):
        return self.name

class Settings(models.Model):
   name = models.CharField(max_length=50)
   stuns_on = models.BooleanField(default=False)
   deactivation_time = models.DurationField(default=timedelta(seconds=8))
   trigger_lockout_delay = models.DurationField(default=timedelta(milliseconds=0))
   reloads_on = models.BooleanField(default=True)

   class Meta:
       verbose_name = "Settings"
       verbose_name_plural = "Settings"

   def __str__(self):
        return self.name

class Site(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100, choices=COUNTRIES)
    address = models.CharField(max_length=200)
    system = models.ForeignKey(System, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

class Tournament(models.Model):
    name =  models.CharField(max_length=200)
    site = models.ForeignKey(Site, on_delete=models.PROTECT)
    start_date = models.DateField("Event date", db_index=True)
    end_date = models.DateField("Event date", db_index=True)
    system = models.ForeignKey(System, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

class Event(models.Model):
    start_time = models.DateTimeField("Event start")
    end_time = models.DateTimeField("Event end", null=True, blank=True)
    points_cap = models.IntegerField(default=30, null=True, blank=True)
    format = models.CharField(max_length=50)
    tournament = models.ForeignKey(Tournament, on_delete=models.PROTECT, related_name="events")
    settings = models.ForeignKey(Settings, on_delete=models.PROTECT)

    def __str__(self):
        return self.format

class Team(models.Model):
    name = models.CharField(max_length=50)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Registration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.PROTECT, db_index=True, null=True, blank=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.event} : {self.player}"

class Pass(models.Model):
    PASS_TYPE_CHOICES = [
        ('monthly', 'Monthly Pass'),
        ('season', 'Season Pass'),
    ]
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    pass_type = models.CharField(max_length=20, choices=PASS_TYPE_CHOICES)
    purchase_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()
    price_paid = models.DecimalField(max_digits=8, decimal_places=2)

    @property
    def is_active(self):
        return self.start_date <= timezone.now().date() <= self.end_date

    class Meta():
        verbose_name = "Pass"
        verbose_name_plural = "Passes"

    def __str__(self):
        return f"{self.player} : {self.pass_type}"
