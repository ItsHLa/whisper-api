from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers  import NestedDefaultRouter
from .views import *

router = DefaultRouter()

router.register('folders', FolderViewSet, basename='folders')
router.register('', ChatViewSet, basename='chats')


urlpatterns = [
    path('', include(router.urls)),
]