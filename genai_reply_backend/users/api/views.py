from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from genai_reply_backend.users.api.serializers_jwt import JWTLoginSerializer
from genai_reply_backend.users.api.serializers_jwt import TokenRefreshSerializer
from genai_reply_backend.users.models import User

from .serializers import UserSerializer


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "pk"

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class JWTLoginView(generics.GenericAPIView):
    """JWT 登入 API - 接收帳號密碼，返回 access/refresh token"""

    serializer_class = JWTLoginSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="使用者登入",
        description="使用 email 和 password 登入，成功後返回 JWT tokens",
        examples=[
            OpenApiExample(
                "登入範例",
                value={
                    "email": "user@example.com",
                    "password": "your_password",
                },
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        """處理使用者登入請求"""
        serializer = self.get_serializer(
            data=request.data, context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        # 生成 token 並回傳使用者資訊
        token_data = serializer.save()

        return Response({
            "success": True,
            "message": "登入成功",
            "data": token_data,
        }, status=status.HTTP_200_OK)


class TokenRefreshView(generics.GenericAPIView):
    """JWT Token 刷新 API - 使用 refresh token 取得新的 access token"""

    serializer_class = TokenRefreshSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="刷新 Access Token",
        description="使用 refresh token 取得新的 access token",
        examples=[
            OpenApiExample(
                "Token 刷新範例",
                value={
                    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                },
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        """處理 token 刷新請求"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response({
            "success": True,
            "message": "Token 刷新成功",
            "data": {
                "access": serializer.validated_data["access"],
                "token_type": "Bearer",
            },
        }, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    """登出 API - 將 refresh token 加入黑名單"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="使用者登出",
        description="將 refresh token 加入黑名單，實現安全登出",
        examples=[
            OpenApiExample(
                "登出範例",
                value={
                    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                },
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        """處理使用者登出請求"""
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({
                    "success": False,
                    "message": "請提供 refresh token",
                }, status=status.HTTP_400_BAD_REQUEST)

            # 將 refresh token 加入黑名單
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({
                "success": True,
                "message": "登出成功",
            }, status=status.HTTP_200_OK)

        except TokenError:
            return Response({
                "success": False,
                "message": "無效的 refresh token",
            }, status=status.HTTP_400_BAD_REQUEST)
