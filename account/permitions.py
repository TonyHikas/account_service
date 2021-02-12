from rest_framework.permissions import BasePermission, SAFE_METHODS


class Confirmed(BasePermission):

    message = 'Пользователь не подтверждён'

    def has_permission(self, request, view):
        return request.user.confirmed is True


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsAdmin(BasePermission):
    message = 'Доступ только администраторам'

    def has_permission(self, request, view):
        return request.user.is_superuser is True
