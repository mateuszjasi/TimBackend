from rest_framework.permissions import BasePermission, OR


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser

class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff

class IsAdminOrOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or obj == request.user