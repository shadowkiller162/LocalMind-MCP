# genai_reply_backend/users/permissions.py
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from genai_reply_backend.users.models import User


class IsAdminUser(permissions.BasePermission):
    """僅允許 admin 角色使用者訪問"""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return (
            request.user.is_authenticated and
            request.user.role == User.Role.ADMIN
        )


class IsStaffOrAdmin(permissions.BasePermission):
    """允許 staff 或 admin 角色使用者訪問"""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return (
            request.user.is_authenticated and
            request.user.role in [User.Role.STAFF, User.Role.ADMIN]
        )


class IsOwnerOrStaff(permissions.BasePermission):
    """允許資源擁有者或 staff/admin 訪問"""

    def has_object_permission(self, request: Request, view: APIView, obj) -> bool:
        # 如果是 staff 或 admin，允許所有操作
        if request.user.role in [User.Role.STAFF, User.Role.ADMIN]:
            return True

        # 如果是一般使用者，只能操作自己的資源
        return hasattr(obj, "user") and obj.user == request.user


class IsVerifiedUser(permissions.BasePermission):
    """僅允許已驗證 email 的使用者訪問"""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return (
            request.user.is_authenticated and
            request.user.is_verified
        )
