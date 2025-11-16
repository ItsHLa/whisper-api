from rest_framework import serializers

from a_rtchat.models import GroupChat
from django.contrib.auth import get_user_model

User = get_user_model()
  

class BaseGroupManagementSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(
        queryset = User.objects.all().values_list("id", flat=True),
        required = True,
        write_only=True,
        many = True
    )
    
    class Meta:
        model = GroupChat
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
        
        if group.check_if_admin(users):
            raise serializers.ValidationError({'admins' : ['Admins with this accounts already exists']})
       
        group.add_admins(users)
    
    def remove_users(self,):
        users = self.validated_data['users']
        group = self.validated_data['group']
        
        if not group.check_if_admin(users):
            raise serializers.ValidationError({'admins' : ['Admins with this accounts dose not exists']})
        group.remove_admins(users)

class MembersSerializer(BaseGroupManagementSerializer):
    
    def add_users(self):
        group = self.validated_data['group']
        users = self.validated_data['users']
        if group.members.filter(id__in = users).exists():
            raise serializers.ValidationError({'members' : 'Members with this accounts already exists'})
        group.members.add(*users)
    
    def remove_users(self):
        group = self.validated_data['group']
        users = self.validated_data['users']
        if not group.members.filter(id__in = users).exists():
            raise serializers.ValidationError({'members' : 'Members with this accounts dose not exists'})
        group.members.remove(*users)