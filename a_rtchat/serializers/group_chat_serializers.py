from rest_framework import serializers
from a_rtchat.models import GroupChat
from djoser.serializers import UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()
  
class PublicGroupChatSerializer(serializers.ModelSerializer): 
    members = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = GroupChat
        fields = ('id', 'name', 'description', 'is_private', 'created_at', 'members_count', 'members', 'online_count' )

class PrivateGroupChatSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()    
    
    class Meta:
        model = GroupChat
        fields = ('id', 'name',  'is_private', 'other_user', 'created_at', ) 
        
    def get_other_user(self, obj):
        if obj.is_private:
            me = self.context['request'].user
            other = obj.members.exclude(id=me.id).first()
            return UserSerializer(other).data
        return None
        
    def get_name(self, obj):
        if obj.is_private:
            user = self.context['request'].user
            other = obj.members.exclude(id=user.id).first()
            return f'{other.first_name} {other.last_name}'  
        return None      

class ChatRepresentationMixin:
    def to_representation(self, instance):
        if instance.is_private:
            return PrivateGroupChatSerializer(instance, context=self.context).data
        return PublicGroupChatSerializer(instance, context=self.context).data

# CREATE _ GET
class ChatGroupSerializer(ChatRepresentationMixin, serializers.ModelSerializer,): 
    other_user = serializers.PrimaryKeyRelatedField(
        required = False,
        write_only=True,
        queryset = User.objects.all()
    )
    
    def validate(self, attrs):
        is_private = attrs.get('is_private', False)
        other_user = attrs.get('other_user',None)
        
        if  other_user and 'is_private' not in attrs:
            raise serializers.ValidationError({"is_private" : ["This field is required for private chat."]})
        
        if is_private and not 'other_user' in attrs:
                raise serializers.ValidationError({"other_user" : ["This field is required for private chat."]})
        
        if "name" not in attrs and not is_private:
                raise serializers.ValidationError({"name" : ["This field is required for public chat."]})
            
        return super().validate(attrs)
    
    class Meta:
        model = GroupChat
        fields = ('id', 'tag', 'name', 'description', 'is_private',  'other_user')
        
    def create_public_group(self, validated_data):
        user = self.context['request'].user
        group = GroupChat.objects.create(**validated_data, owner=user)
        group.create_admins_group()
        group.add_admins([group.owner.id])
        group.members.add(group.owner)
        return group
    
    def create_private_group(self, validated_data):
        user = user = self.context['request'].user
        other_user = validated_data.pop('other_user', None)
        group, created = GroupChat.objects.get_or_create(**validated_data)
        if created:
            group.members.add(user, other_user)
        return group
    
    def create(self, validated_data):
        is_private = validated_data.get('is_private', False)
        if is_private:
            return self.create_private_group(validated_data)
        else:
            return self.create_public_group(validated_data)
                
# UPDATE
class UpdatePublicGroupChatSerializer(ChatRepresentationMixin, serializers.ModelSerializer,):
    name = serializers.CharField(required = False)
    
    class Meta:
        model = GroupChat
        fields = ('tag', 'name', 'description',)
    
#LIST
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
