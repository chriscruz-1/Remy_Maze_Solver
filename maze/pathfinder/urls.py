from os import name
from pathfinder.views import fetch_map
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name='index'),
    path("fetch_model", views.fetch_model, name='fetch_model'),
    path("fetch_map", views.fetch_map, name='fetch_map'),
    path('info', views.info, name='info'),
    path("<str:name>", views.greet, name='greet'),
]
