from django.shortcuts import render
from django.views.generic import TemplateView


class ChatTestView(TemplateView):
    """
    AI 對話測試頁面
    提供簡單的網頁介面來測試 AI 對話功能
    """
    template_name = "chat/test.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page_title": "AI 對話測試",
            "description": "測試 MaiAgent AI 對話功能的網頁介面",
        })
        return context


def chat_test(request):
    """
    Function-based view for chat testing
    """
    context = {
        "page_title": "AI 對話測試",
        "description": "測試 MaiAgent AI 對話功能的網頁介面",
    }
    return render(request, "chat/test.html", context)
