from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("editEntry/<str:titleParm>/", views.editEntry, name="editEntry"),
    path("randomPage", views.randomPage, name="randomPage"),
    path("wiki/<str:titleParm>", views.loadTitlePage, name="title"),

]


