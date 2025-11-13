from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # auth
    path('api/', include('a_users.urls')),
    path('api/', include("djoser.urls")),
    
    #GroupChat
    path('api/chats/', include('a_rtchat.urls')),
]
