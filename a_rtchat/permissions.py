from rest_framework import permissions
from .models import *
from django.shortcuts import get_object_or_404

class IsGroupAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return not obj.is_private and obj.check_if_admin([request.user.id]) and obj.is_member([request.user.id])

class IsGroupOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        pk = view.kwargs.get('pk')
        group = get_object_or_404(GroupChat, id=pk, is_private=False)
        return group.owner == request.user

class IsGroupMember(permissions.BasePermission):
    def has_permission(self, request, view):
        pk = view.kwargs.get("pk")
        group = get_object_or_404(GroupChat, id=pk, is_private=False)
        return group.members.filter(id = request.user.id).exists()