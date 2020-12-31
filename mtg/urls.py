from django.urls import path
# from .mtg_bert import Bert

from . import views

app_name = 'mtg'
# model = get_model()
urlpatterns = [
    path('', views.index, name="index"),
    # path('', views.DetailView.as_view(), name="index"),
    path('call_model', views.call_model, name="call_model")
    # path('<str:card_name>/action', views.action, name='action')
]
