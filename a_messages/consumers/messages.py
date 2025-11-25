from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from a_chats.models.chat import *
from a_messages.models.chat_messages import ChatMessage
from a_messages.serializers.chat_message import *
from asgiref.sync import async_to_sync
import json


class MessagesWebsocketConsumer(WebsocketConsumer):
    
    def connect(self):
        try:
            kwargs = self.scope['url_route']['kwargs']
        # get pk from scope kwargs
            pk = kwargs['pk']
        # get chat
            self.chat = get_object_or_404(Chat, id=pk)
        # get user from scope
            self.user = None
            # print(self.channel_name)
            print(self.chat.uid)
        # create channel for each websocket connection using unique uuid
            async_to_sync(self.channel_layer.group_add)(
            f'chat{self.chat.pk}', # group-name
            self.channel_name,
        )
           
            self.accept()
        except Exception as e:
            print(f"WebSocket REJECT: {str(e)}")
            self.close()
        
    
    def send_message(self, event):
        
        self.send(json.dumps({
            "msg" :event['msg']
        }))
        return
    
    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        self.user = get_object_or_404(User, id=2)
        # create messags
        msg = ChatMessage.objects.create(
            chat = self.chat,
            user=self.user,
            **data)
        
        # serializer message
        serializer = ChatMessageSerializer(msg)
        
        # send msg to group
        async_to_sync(self.channel_layer.group_send(
            self.chat.uid,
            {
                'type' : 'send.message',
                'msg' : serializer.data
            }
        ))
        return 
    
    def disconnect(self, code):
        pass
        # async_to_sync(self.channel_layer.group_discard(
        #     self.chat.uid,
        #     self.channel_name
        # ))