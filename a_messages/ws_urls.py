from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers  import NestedDefaultRouter
from .consumers.messages import *



websocket_urlpatterns = [
    path('ws/chats/<str:pk>/messages/', MessagesWebsocketConsumer.as_asgi() )
]