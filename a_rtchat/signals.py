from django.dispatch import receiver
from django.db.models.signals import post_delete
from .models import *

@receiver(post_delete, sender=GroupChat)
def delete_group_admin(sender, instance,  **kwargs):
    instance.delete_admin_group()