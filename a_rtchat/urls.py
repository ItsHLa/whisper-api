from django.urls import include, path
from rest_framework_nested import routers
from .views import *

router = routers.DefaultRouter()

router.register('groups', GroupChatViewSet, basename='list-create-group-chat')


urlpatterns = [
    path('', include(router.urls)),
    
]