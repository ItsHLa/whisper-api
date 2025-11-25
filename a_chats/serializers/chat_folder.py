from rest_framework import serializers
from a_chats.models.chat_folder import ChatFolder, Folder
from a_chats.models.chat import Chat

class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ('id', 'name',)

class FolderRepresentationMixin:
    def to_representation(self, instance):
        return FolderSerializer(instance, context=self.context).data

class CreateChatFolderSerializer(FolderRepresentationMixin, serializers.ModelSerializer):
    chats = serializers.PrimaryKeyRelatedField(
        required = True,
        many= True,
        write_only=True ,
        queryset= Chat.objects.all()
    )
    
    class Meta:
        model = Folder
        fields = ('name', 'chats', )
    
    def create(self, validated_data):
        user = self.context['request'].user
        chats = validated_data.pop('chats', None)
        folder = Folder.objects.create(
            user= user,
            **validated_data)
        chat_folders= [
            ChatFolder(
                chat=chat, folder=folder) for chat in chats
            ]   
        ChatFolder.objects.bulk_create(chat_folders)
        return folder
      
class UpdateChatFolderSerializer(FolderRepresentationMixin, serializers.ModelSerializer):
    name = serializers.CharField(required= True)
    
    class Meta:
        model = Folder
        fields =  ('name',)
