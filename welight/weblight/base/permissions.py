from rest_framework import permissions

class UserRolePermission(permissions.BasePermission):
    """
    This permission class allows or denies access to views based on the roles assigned to users.

    Roles:
        - 'manage': Users with this role can perform 'POST' and 'DELETE' actions.
        - 'admin': Users with this role can perform 'POST' and 'DELETE' actions.
        - 'superadmin': Users with this role can perform 'POST' and 'DELETE' actions.
        - 'employee': Users with this role can perform 'GET', 'PUT', and 'PATCH' actions.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        allowed_roles = ['manage', 'admin', 'superadmin']
        if request.user.role in allowed_roles:
            if request.method in ['POST', 'DELETE','GET', 'PUT', 'PATCH']:
                return True
        elif request.user.role == 'employee':
            if request.method in ['GET', 'PUT', 'PATCH']:
                return True
        return False
