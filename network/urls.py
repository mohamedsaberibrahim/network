
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("following", views.following, name="following"),
    path("follow/<int:profile_id>", views.follow, name="follow"),
    path("profile/<int:profile_id>", views.profile, name="profile"),
    
    # API routes
    path("addpost", views.addpost, name="addpost"),
    path("edit/<int:post_id>", views.edit, name="edit"),
    path("like/<int:post_id>", views.like, name="like"),
    path("posts/<int:post_id>", views.post, name="post")
]
