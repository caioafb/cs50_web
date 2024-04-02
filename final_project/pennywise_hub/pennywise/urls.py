from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("new_transaction", views.new_transaction, name="new_transaction"),
    path("settings", views.settings, name="settings"),
    path("archive", views.archive, name="archive")
]
