from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name='index'),
    path('info', views.info, name='info'),
    path("<str:name>", views.greet, name='greet'),
]
