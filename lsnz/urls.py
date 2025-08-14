from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("events", views.events, name="events"),
    path("events/<slug:event_slug>", views.event_detail, name="event_detail"),
    path("events/<slug:event_slug>/register", views.event_register, name="event_register"),
    path("events/<slug:event_slug>/deregister", views.event_deregister, name="event_deregister"),
    path("sites", views.sites, name="sites"),
    path("sites/<slug:site_slug>", views.site_detail, name="site_detail"),
    path("players", views.players, name="players"),
    path("players/<str:alias>", views.player_detail, name="player_detail"),
    path("blog", views.blog, name="blog"),
    path("blog/<int:page>", views.blog, name="blog"),
    path("blog/post/<slug:post_slug>", views.post_detail, name="post_detail"),
    path("write", views.write_post, name="write_post"),
    path("edit/<slug:post_slug>", views.edit_blog_post, name="edit_blog_post"),
    path("profile/edit", views.edit_profile, name="edit_profile"),
    path("about", views.about, name="about"),
    path("privacy", views.privacy, name="privacy"),
    path("terms", views.terms, name="terms"),
]
