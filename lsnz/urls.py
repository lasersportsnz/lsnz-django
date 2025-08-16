from django.urls import path

from . import views
from .views import (PlayerListView, PlayerDetailView, PlayerUpdateView,
    PostListView, PostDetailView, PostCreateView, PostUpdateView,
    SiteDetailView, SiteListView,
    TournamentDetailView, TournamentListView,TournamentRegistrationView,
    SystemListView, SystemDetailView)

app_name = "lsnz"

urlpatterns = [
    path("", views.index, name="index"),
    path("tournaments", TournamentListView.as_view(), name="tournaments"),
    path("tournaments/<slug:slug>", TournamentDetailView.as_view(), name="tournament_detail"),
    path("tournaments/<slug:slug>/register", TournamentRegistrationView.as_view(), name="tournament_register"),
    path("systems", SystemListView.as_view(), name="systems"),
    path("systems/<slug:slug>", SystemDetailView.as_view(), name="system_detail"),
    path("sites", SiteListView.as_view(), name="sites"),
    path("sites/<slug:slug>", SiteDetailView.as_view(), name="site_detail"),
    path("players", PlayerListView.as_view(), name="players"),
    path("players/<slug:slug>", PlayerDetailView.as_view(), name="player_detail"),
    path("players/<slug:slug>/edit", PlayerUpdateView.as_view(), name="edit_profile"),
    path("blog", PostListView.as_view(), name="blog"),
    path("blog/<slug:slug>", PostDetailView.as_view(), name="post_detail"),
    path("write", PostCreateView.as_view(), name="write_post"),
    path("edit/<slug:slug>", PostUpdateView.as_view(), name="edit_blog_post"),
    path("about", views.about, name="about"),
    path("privacy", views.privacy, name="privacy"),
    path("terms", views.terms, name="terms"),
]
