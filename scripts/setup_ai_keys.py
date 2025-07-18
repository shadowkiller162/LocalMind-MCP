#!/usr/bin/env python3
"""
AI API 金鑰設定與測試腳本
"""
import os
import sys

import django

# 設定 Django 環境
sys.path.append("/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from core.services.anthropic_service import AnthropicService
from core.services.factory import AIServiceFactory
from core.services.google_service import GoogleService
from core.services.openai_service import OpenAIService

# Constants
MASK_LENGTH = 8


def check_environment_variables():
    """檢查環境變數設定"""
    print("🔍 檢查環境變數設定...")  # noqa: T201

    env_vars = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "ENABLED_AI_SERVICES": os.getenv(
            "ENABLED_AI_SERVICES", "openai,anthropic,google",
        ),
        "DEFAULT_AI_SERVICE": os.getenv("DEFAULT_AI_SERVICE", "openai"),
    }

    print("\n環境變數狀態:")  # noqa: T201
    for key, value in env_vars.items():
        if value:
            masked_value = (
                f"{value[:MASK_LENGTH]}..." if len(value) > MASK_LENGTH else value
            )
            print(f"  ✅ {key}: {masked_value}")  # noqa: T201
        else:
            print(f"  ❌ {key}: 未設定")  # noqa: T201

    return env_vars


def _test_ai_service(service_name, service_class, config_key, test_messages):
    """測試單一 AI 服務"""
    from django.conf import settings

    api_key = os.getenv(f"{service_name.upper()}_API_KEY")
    if not api_key:
        return

    print(f"\n🔸 測試 {service_name} 服務...")  # noqa: T201
    service = service_class(settings.AI_SERVICES_CONFIG[config_key])

    if service.is_available():
        try:
            response = service.generate_response(test_messages)
            if response.is_success:
                print(f"  ✅ {service_name} 回應: {response.content[:100]}...")  # noqa: T201
                print(f"  📊 使用 tokens: {response.tokens_used}")  # noqa: T201
            else:
                print(f"  ❌ {service_name} 錯誤: {response.error}")  # noqa: T201
        except Exception:  # noqa: BLE001
            print(f"  ❌ {service_name} 服務發生錯誤")  # noqa: T201
    else:
        print(f"  ⚠️  {service_name} 服務不可用")  # noqa: T201


def test_individual_services():
    """測試個別 AI 服務"""
    print("\n🧪 測試個別 AI 服務...")  # noqa: T201

    test_messages = [
        {
            "role": "system",
            "content": "你是一個友善的 AI 助手，請用繁體中文回答。",
        },
        {
            "role": "user",
            "content": "你好！請簡短介紹自己。",
        },
    ]

    # 測試各個 AI 服務
    _test_ai_service("OpenAI", OpenAIService, "OPENAI", test_messages)
    _test_ai_service("Anthropic", AnthropicService, "ANTHROPIC", test_messages)
    _test_ai_service("Google", GoogleService, "GOOGLE", test_messages)


def test_factory_service():
    """測試工廠服務和容錯機制"""
    print("\n🏭 測試 AI 服務工廠和容錯機制...")  # noqa: T201

    test_messages = [
        {
            "role": "user",
            "content": "請告訴我現在的時間，如果無法取得，請回答『我無法取得當前時間』",
        },
    ]

    try:
        # 測試工廠建立服務
        ai_service = AIServiceFactory.create_service()
        print(f"  📝 選擇的服務: {ai_service.get_service_name()}")  # noqa: T201

        # 測試回應生成
        response = ai_service.generate_response(test_messages)

        if response.is_success:
            print(f"  ✅ 工廠服務回應: {response.content[:100]}...")  # noqa: T201
            print(f"  📊 使用模型: {response.model}")  # noqa: T201
            print(f"  📊 使用 tokens: {response.tokens_used}")  # noqa: T201
        else:
            print(f"  ❌ 工廠服務錯誤: {response.error}")  # noqa: T201

    except Exception:  # noqa: BLE001
        print("  ❌ 工廠服務發生錯誤")  # noqa: T201


def test_celery_integration():
    """測試 Celery 整合"""
    print("\n⚙️ 測試 Celery 整合...")  # noqa: T201

    try:
        from core.tasks import generate_ai_response

        # 測試 AI 回應生成函數
        context = []
        user_message = "你好！請簡短測試回應。"

        response = generate_ai_response(context, user_message)
        print(f"  ✅ Celery 整合測試: {response[:100]}...")  # noqa: T201

    except Exception:  # noqa: BLE001
        print("  ❌ Celery 整合發生錯誤")  # noqa: T201


def main():
    """主要執行函數"""
    print("🚀 AI 服務金鑰設定與測試")  # noqa: T201
    print("=" * 50)  # noqa: T201

    # 檢查環境變數
    env_vars = check_environment_variables()

    # 如果沒有設定任何 API 金鑰，顯示設定指南
    required_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"]
    if not any(env_vars[key] for key in required_keys):
        print("\n⚠️  尚未設定任何 API 金鑰！")  # noqa: T201
        print("\n📋 設定步驟:")  # noqa: T201
        print("1. 編輯 .envs/.local/.django 檔案")  # noqa: T201
        print("2. 設定對應的 API 金鑰")  # noqa: T201
        print("3. 重新啟動 Docker 容器")  # noqa: T201
        print("4. 再次執行此腳本")  # noqa: T201
        return

    # 測試個別服務
    test_individual_services()

    # 測試工廠服務
    test_factory_service()

    # 測試 Celery 整合
    test_celery_integration()

    print("\n🎉 測試完成！")  # noqa: T201
    print("=" * 50)  # noqa: T201


if __name__ == "__main__":
    main()
