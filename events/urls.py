from django.urls import path
from . import views

app_name = "events"
urlpatterns = [
    path("", views.home, name="home"),
    path("<str:code>/edit/", views.edit_event, name="edit"),
    path("<str:code>/delete/", views.delete_event_view, name="delete"),
]

