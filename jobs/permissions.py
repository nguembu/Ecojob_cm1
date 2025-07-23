from rest_framework.permissions import BasePermission

class IsRecruiter(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Recruteur'

class IsCollector(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'collector'


