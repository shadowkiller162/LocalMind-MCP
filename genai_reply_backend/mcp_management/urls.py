"""
MCP Management URL Configuration
"""

from django.urls import path
from . import views

app_name = "mcp_management"

urlpatterns = [
    path("", views.mcp_dashboard, name="dashboard"),
    path("status/", views.mcp_status, name="status"),
    path("reconnect/", views.mcp_reconnect, name="reconnect"),
    path("chat/send/", views.chat_send, name="chat_send"),
    path("chat/regenerate/", views.chat_regenerate, name="chat_regenerate"),
]