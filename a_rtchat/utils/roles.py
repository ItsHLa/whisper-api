from django.contrib.auth.models import Group

class Role:
    
    def get_create_group(group_name):
        return Group.objects.get_or_create(name= group_name)
    
    @classmethod
    def set(cls, uid, user):
        group, created = cls.get_create_group(uid)
        user.groups.add(group)