from rest_framework import serializers

from a_chats.models.chat import Chat
from a_chats.models.chat_messages import *
from django.contrib.auth import get_user_model

User = get_user_model()

class PublicMemberSerializer(serializers.Serializer):
    name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    last_seen = serializers.SerializerMethodField()
    
    def get_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'
    
    def get_role(self, obj):
        print(obj)
        role = 'member'
        if obj.user_membership.filter(is_admin=True).exists():
            role = 'admin'
        if obj.user_membership.filter(is_owner=True).exists():
            role = 'owner'
        return role
    
    def get_last_seen(self, obj):
        return None
    
class PrivateMemberSerializer(serializers.Serializer):
    name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    last_seen = serializers.SerializerMethodField()
    
    def get_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'
    
    def get_role(self, obj):
        print(obj)
        role = 'member'
        if obj.user_membership.filter(is_admin=True).exists():
            role = 'admin'
        if obj.user_membership.filter(is_owner=True).exists():
            role = 'owner'
        return role
    
    def get_last_seen(self, obj):
        return None
  

class BaseGroupManagementSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(
        queryset = User.objects.all(),
        required = True,
        write_only=True,
        many = True
    )
    
    class Meta:
        model = Chat
        fields = ('users',)
    
    def add_users(self):
        raise NotImplementedError("Subclasses must implement add_users()")
    
    def remove_users(self):
        raise NotImplementedError('Subclasses must implement remove_users()')
    
class AdminSerializer(BaseGroupManagementSerializer):
       
    def add_users(self,):
        users = self.validated_data['users']
        group = self.validated_data['group']
        
        if group.is_private:
            raise serializers.ValidationError({'admins' : ['Only public groups can have admins']})
        
        if not group.are_members(users):
            raise serializers.ValidationError({'admins' : ['To ba an admin user should be member in group']})
        
        if group.are_admins(users):
            raise serializers.ValidationError({'admins' : ['Admins with this accounts already exists']})
       
        group.add_admins(users)
    
    def remove_users(self,):
        users = self.validated_data['users']
        group = self.validated_data['group']
        
        if not group.are_admins(users):
            raise serializers.ValidationError({'admins' : ['Admins with this accounts dose not exists']})
        group.remove_admin(users)

class MembershipSerializer(BaseGroupManagementSerializer):
    
    
    def add_users(self):
        group = self.validated_data['group']
        users = self.validated_data['users']
        if group.are_members(users):
            raise serializers.ValidationError({'members' : 'Members with this accounts already exists'})
        group.add_members(users)
    
    def remove_users(self):
        group = self.validated_data['group']
        users = self.validated_data['users']
        if not group.are_members(users):
            raise serializers.ValidationError({'members' : 'Members with this accounts dose not exists'})
        group.remove_membership(users)