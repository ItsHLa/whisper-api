from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import *
from a_rtchat.permissions import *
from a_rtchat.serializers.group_chat_serializers import *
from a_rtchat.serializers.membership_serializers import *
from django.shortcuts import get_object_or_404
from .models import *
     
class GroupChatViewSet(ModelViewSet):
    
    def get_serializer_class(self):
        print(self.action)
        
        if self.action == 'partial_update':
            return UpdatePublicGroupChatSerializer
        
        if self.action == "list":
            return ListGroupChatSerializer

        return ChatGroupSerializer  
    
    def get_queryset(self):
        if self.action == 'join':
            return GroupChat.objects.all()
        return GroupChat.objects.filter(members=self.request.user).prefetch_related("members", "group_messages")
    
    def get_permissions(self):
        if self.action in ['destroy', 'remove_admins', 'add_admins' ] :
            return [IsAuthenticated(), IsGroupOwner()]
        if self.action in ['get', 'add_members']:
            return [IsAuthenticated(), IsGroupMember()]
        if self.action in ['join', 'create']:
            return [AllowAny()]
        return [IsAuthenticated(), IsGroupAdmin()]
    
    
    @action(detail=True, methods=['post'] )
    def join(self, request, pk):
        group = get_object_or_404(GroupChat, id=pk, is_private=False)
        group.members.add(request.user)
        return Response(status= HTTP_200_OK)
    
    # Member + list, get
    @action(detail=True, methods=['post'])
    def add_members(self, request, pk):
        group = get_object_or_404(GroupChat, id=pk, is_private = False)
        serializer = MembersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['group'] = group
        serializer.add_users() 
        return Response(status= HTTP_200_OK)
               
    @action(detail=True, methods=['delete'],)
    def remove_admins(self, request, pk):
        object = get_object_or_404(GroupChat, id=pk, is_private = False)
        serializer = AdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['group'] = object
        serializer.remove_users()
        return Response(status= HTTP_200_OK)
    
    @action(detail=True, methods=['patch'],)
    def add_admins(self, request, pk):
        object = get_object_or_404(GroupChat, id=pk, is_private = False)
        serializer = AdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['group'] = object
        serializer.add_users()
        return Response(status= HTTP_200_OK)
 
    @action(detail=True, methods=['delete'])
    def remove_members(self, request, pk):
        group = self.get_object()
        serializer = MembersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['group'] = group
        serializer.remove_users() 
        return Response(status= HTTP_200_OK)
    
