from rest_framework import serializers
from .models import *
from djoser.serializers import UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()
  
class PublicGroupChatSerializer(serializers.ModelSerializer): 
    members = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = GroupChat
        fields =   ('id', 'name', 'description', 'is_private', 'created_at', 'members_count', 'members', 'online_count' )

class PrivateGroupChatSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()    
    
    class Meta:
        model = GroupChat
        fields =('id', 'name',  'is_private', 'other_user', 'created_at', ) 
        
    def get_other_user(self, obj):
        if obj.is_private:
            me = self.context['request'].user
            other = obj.members.exclude(id=me.id).first()
            return UserSerializer(other).data
        
    def get_name(self, obj):
        if obj.is_private:
            user = self.context['request'].user
            other = obj.members.exclude(id=user.id).first()
            return f'{other.first_name} {other.last_name}'        
        

class ChatGroupSerializer(serializers.ModelSerializer): 
    other_user = serializers.PrimaryKeyRelatedField(
        required = False,
        write_only=True,
        queryset = User.objects.all()
    )
    
    # def validate(self, attrs):
        
    #     errors = self.validate_chat_data(attrs, self.context['request'])
    #     if errors:
    #         raise serializers.ValidationError(errors)
    #     return super().validate(attrs)
    
    class Meta:
        model = GroupChat
        fields = ('id', 'tag', 'name', 'description', 'is_private',  'other_user')
    
    def to_representation(self, instance):
        if instance.is_private:
            return PrivateGroupChatSerializer(instance, context=self.context).data
        return PublicGroupChatSerializer(instance, context =self.context).data
        
    def create_public_group(self, validated_data):
        group = GroupChat.objects.create(**validated_data)
        group.create_admins_group()
        group.add_admin(group.owner)
        group.members.add(group.owner)
        return group
    
    def create_private_group(self, validated_data):
        user = validated_data.pop('user', None)
        other_user = validated_data.pop('other_user', None)
        group, created = GroupChat.objects.get_or_create(**validated_data)
        
        group.members.add(user, other_user)
        return group
    
    def create(self, validated_data):
        user = self.context['request'].user
        is_private = validated_data.get('is_private', False)
        if is_private:
            if not validated_data.get('other_user'):
                raise serializers.ValidationError({
                    'other_user' : ["This field is required."]
                })
            validated_data['user'] = user
            return self.create_private_group(validated_data)
        else:
            validated_data['owner'] = user
            return self.create_public_group(validated_data)
 
class ListGroupChatSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    
    class Meta:
        model = GroupChat
        fields =('id', 'tag', 'name',  'is_private', 'last_message' )
    
    def get_name(self, obj):
        if obj.is_private:
            me = self.context['request'].user
            other = obj.members.exclude(id=me.id).first()
            return f"{other.first_name} {other.last_name}" 
        return obj.name
           
    def get_last_message(self, obj):
        msg= obj.group_messages.all().first()
        return str(msg.body) if msg else None

class AdminSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset = User.objects.all(),
        required = True,
        write_only=True,
    )
    
    def add_admin(self,):
        user = self.validated_data['user']
        group = self.validated_data['group']
        if GroupChat.is_user_admin_in(user, group):
            raise serializers.ValidationError({'admin' : ['Admin with this account already exists']})
        group.add_admin(user)
    
    def remove_admin(self,):
        user = self.validated_data['user']
        group = self.validated_data['group']
        if not GroupChat.is_user_admin_in(user, group):
            raise serializers.ValidationError({'admin' : ['Admin with this account dose not exists']})
        group.remove_admin(user)
        