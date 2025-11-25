from django.db import models
from django.contrib.auth import get_user_model

from a_chats.models.chat import Chat

User = get_user_model()

class Folder(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, related_name='user_folders', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    chats = models.ManyToManyField('Chat', related_name='folders', through='ChatFolder', through_fields=['folder', 'chat'])
    is_empty = models.BooleanField(default=False)
    

class  ChatFolder(models.Model):
    chat = models.ForeignKey('Chat', related_name='chats_folder', on_delete=models.CASCADE)
    folder = models.ForeignKey('Folder', related_name='folder_chats', on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['chat', 'folder']  
        indexes = [models.Index(fields=['chat', 'folder'], name='chat_folder_idx')  ] 