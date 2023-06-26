from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsManagerOrReadOnlyPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if request.method in SAFE_METHODS:
            return True

        return user.is_superuser or user.groups.filter(name="manager").exists()
