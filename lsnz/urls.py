from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("events", views.events, name="events"),
    path("sites", views.sites, name="sites"),
    path("players", views.players, name="players"),

]