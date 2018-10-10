from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("prospects", views.FilteredNetworkList.as_view(), name="prospects"),
]
