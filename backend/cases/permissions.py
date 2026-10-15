from rest_framework.permissions import BasePermission, SAFE_METHODS


def is_admin(user):
    return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser or user.groups.filter(name="Administrator").exists()))


def is_lawyer(user):
    return bool(user and user.is_authenticated and user.groups.filter(name="Lawyer").exists())


class CasePermission(BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if is_admin(user):
            return True
        if is_lawyer(user):
            return obj.lawyer_id == user.id and request.method in SAFE_METHODS
        return obj.client_id == user.id and request.method in SAFE_METHODS
