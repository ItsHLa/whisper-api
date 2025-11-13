from rest_framework import permissions

class IsGroupAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            if not obj.is_private:
                return obj.is_admin(request.user)
        return True