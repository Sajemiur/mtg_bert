from django.urls import path
from . import views

app_name = 'mtg'

urlpatterns = [
    path('', views.index, name="index"),
]
