from django.db import models
from a_chats.models.public_group_membership import ChatMembership

class ChatManager(models.Manager):
    
    def create_private_group(self, data):
        print(data)
        members = data.pop('members', None)
        print(data)
        chat, created = super().get_or_create(**data)
        if created:
            chat.add_members(members)
        return chat
    
    def create_public_group(self, data):
        print(data)
        owner = data.pop('user', None)
        print(data)
        chat = super().create(**data)
        chat.add_owner(owner)
        return chat