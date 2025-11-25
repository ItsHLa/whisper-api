from django.contrib import admin

from a_chats.models.chat_folder import *
from a_chats.models.chat import Chat
from a_chats.models.chat import ChatMembership


admin.site.register(Chat)
admin.site.register(ChatMembership)

admin.site.register(Folder)
admin.site.register(ChatFolder)

