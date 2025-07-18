# genai_reply_backend/users/api/urls.py
from django.urls import path

from genai_reply_backend.users.api.views import JWTLoginView
from genai_reply_backend.users.api.views import LogoutView
from genai_reply_backend.users.api.views import TokenRefreshView

app_name = "users_api"

urlpatterns = [
    # JWT 認證相關 endpoints
    path("auth/login/", JWTLoginView.as_view(), name="jwt-login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("auth/logout/", LogoutView.as_view(), name="jwt-logout"),
]
