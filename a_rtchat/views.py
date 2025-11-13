from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import *
from a_rtchat.permissions import IsGroupAdmin
from a_rtchat.utils.roles import Role
from .models import *
from .serializes import *

class GroupChatViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsGroupAdmin]
    
    
    def get_serializer_class(self):
        
        if self.action == "list":
            return ListGroupChatSerializer
        # if self.action == 'retrieve':
        #     return RetrieveGroupChatSerializer
        return ChatGroupSerializer
    
    def get_queryset(self):
        if self.action == 'join':
            return GroupChat.objects.all()
        return GroupChat.objects.filter(members=self.request.user).prefetch_related("members", "group_messages")
    
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk):
        group = self.get_object()
        group.members.add(request.user)
        return Response(status= HTTP_200_OK)
    
    @action(detail=True, methods=['patch'])
    def add_admin(self, request, pk):
        object = self.get_object()
        serializer = AdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['group'] = object
        serializer.add_admin()
        return Response(status= HTTP_200_OK)
    
    @action(detail=True, methods=['delete'])
    def remove_admin(self, request, pk):
        object = self.get_object()
        serializer = AdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        object.remove_admin()
        return Response(status= HTTP_200_OK)
    
    
    