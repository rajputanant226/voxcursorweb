from django.urls import path
from .views import home, chat, login_view, register_view, logout_view

urlpatterns = [
    path("", home, name="home"),
    path("api/chat/", chat, name="chat"),
    path("login/", login_view, name="login"),
    path("api/register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
]
