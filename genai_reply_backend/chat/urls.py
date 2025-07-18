from django.urls import path

from .views import ChatTestView

app_name = "chat"

urlpatterns = [
    path("test/", ChatTestView.as_view(), name="test"),
]
