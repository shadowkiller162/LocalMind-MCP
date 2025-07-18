# genai_reply_backend/users/api/serializers_jwt.py
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken


class CustomRefreshToken(RefreshToken):
    """自定義 RefreshToken，在 payload 中加入使用者 role 資訊"""

    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        # 加入使用者角色到 JWT payload
        token["role"] = user.role
        token["display_name"] = user.display_name or user.name
        token["is_verified"] = user.is_verified
        return token


class JWTLoginSerializer(serializers.Serializer):
    """JWT 登入 Serializer - 處理帳號密碼驗證與 Token 生成"""

    email = serializers.EmailField(
        help_text="使用者 Email 帳號",
    )
    password = serializers.CharField(
        write_only=True,
        help_text="使用者密碼",
    )

    def validate(self, attrs):
        """驗證使用者帳號密碼"""
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            msg = "請提供完整的 email 與密碼"
            raise serializers.ValidationError(
                msg,
                code="missing_credentials",
            )

        # 使用 Django 內建驗證機制
        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=password,
        )

        if not user:
            msg = "無效的電子郵件或密碼，請檢查後重試"
            raise serializers.ValidationError(
                msg,
                code="invalid_credentials",
            )

        if not user.is_active:
            msg = "此帳號已被停用，請聯繫管理員"
            raise serializers.ValidationError(
                msg,
                code="inactive_user",
            )

        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        """生成 JWT Token 並回傳使用者資訊"""
        user = validated_data["user"]

        # 使用自定義 Token 類別來包含 role 資訊
        refresh = CustomRefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "token_type": "Bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "display_name": user.display_name or user.name,
                "role": user.role,
                "is_verified": user.is_verified,
            },
        }


class TokenRefreshSerializer(serializers.Serializer):
    """Token 刷新 Serializer"""

    refresh = serializers.CharField(
        help_text="Refresh Token",
    )

    def validate(self, attrs):
        refresh = attrs.get("refresh")
        try:
            token = RefreshToken(refresh)
            # 驗證 Token 有效性
            token.verify()
            attrs["access"] = str(token.access_token)
        except Exception as e:
            msg = "無效的 refresh token"
            raise serializers.ValidationError(
                msg,
                code="invalid_token",
            ) from e
        return attrs
