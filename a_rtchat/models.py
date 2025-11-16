from django.db import models
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
import uuid
User = get_user_model()

        
class GroupChat(models.Model):
    tag = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=128, null=True, blank=True)
    description = models.CharField(max_length=300, blank=True, null=True)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    link = models.URLField(null=True, unique=True)
    is_private = models.BooleanField(default=False)
    owner = models.ForeignKey(
        User, 
        blank=True, 
        null=True,
        on_delete=models.SET_NULL,
        related_name='owned_groups' )
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(
        User,
        related_name='group_members')
    online = models.ManyToManyField(
        User,
        blank=True,
        related_name='group_online_members')
    admins = models.OneToOneField(
        Group,
        null=True,
        blank=True,
        related_name='group_admins',
        on_delete=models.SET_NULL)
    
    
    def delete_admin_group(self):
        if self.admins:
            self.admins.delete()
       
    def create_admins_group(self):
        admins, created = Group.objects.get_or_create(name=f"admins_chat_{self.uid}")
        self.admins = admins
        self.save(update_fields=['admins'])
     
    def are_members(self, users):
        return self.members.filter(id__in = users).exists()
        
    def add_admins(self, users):
        if not self.admins :
            self.create_admins_group()
        
        if  self.check_if_admin(users):
            return 
        if isinstance(users,(list, tuple, QuerySet)):
            self.admins.user_set.add(*users)
        else:
            self.admins.user_set.add(users)
    
    def remove_admins(self, users):
        if not self.admins :
            self.create_admins_group()
            
        if self.check_if_admin(users):
            self.admins.user_set.remove(*users)
            
    def check_if_admin(self, users):
        return self.admins and self.admins.user_set.filter(id__in=users).exists()
    
    def is_owner(self, user):
        return self.owner.id == user.id
    
    def is_member(self, users):
        return self.members.filter(id__in=users).exists()
    
    @property
    def members_count(self):
        return self.members.count()
    
    @property
    def online_count(self):
        return self.online.count()
    
    @property
    def admins_users(self):
        if self.admins:
          return self.admins.user_set.all()
        return User.objects.none()
    
    def __str__(self) -> str:
        str = None
        if self.is_private:
            return f"Private {self.id} - {self.uid}"
        return f"Public {self.id} - {self.uid}"
    
class GroupChatMessage(models.Model):
    group = models.ForeignKey(GroupChat, related_name='group_messages', on_delete=models.CASCADE)
    user = models.ForeignKey(
        User,
        related_name='user_messages',
        on_delete=models.SET_NULL,
        null=True, blank=True)
    body = models.TextField()
    # media = models.ImageField()
    seen = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    # received_at = models.DateTimeField()
    reply_to = models.ForeignKey(
        'self',
        related_name='replies',
        blank=True, null=True,
        on_delete=models.SET_NULL )
    
    @property
    def replies_count(self):
        return self.replies.count()
    
    def __str__(self) -> str:
        return f"{self.user.username} : {self.body}"
    
    class Meta:
        ordering = ['-created']