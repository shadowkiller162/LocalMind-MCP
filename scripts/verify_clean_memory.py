#!/usr/bin/env python3
"""
驗證 LM Studio 記憶體是否完全清空的腳本
"""

import sys
import requests
import os
import django

sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from mcp.config import get_config


def verify_clean_memory():
    """驗證 LM Studio 記憶體狀態"""
    
    config = get_config()
    chat_url = f"http://{config.lmstudio_host}:{config.lmstudio_port}/v1/chat/completions"
    
    print("🔍 驗證 LM Studio 記憶體清空狀態")
    print("=" * 50)
    
    try:
        # 測試無指定模型的請求
        response = requests.post(chat_url, json={
            'messages': [{'role': 'user', 'content': 'test'}],
            'max_tokens': 1
        }, timeout=5)
        
        if response.status_code == 404:
            error_data = response.json()
            error_message = error_data.get('error', {}).get('message', '')
            
            if 'Multiple models are loaded' in error_message:
                print("❌ 記憶體未清空")
                print("   仍有多個模型載入，請手動卸載所有模型")
                return False
            elif 'No models loaded' in error_message or 'No model loaded' in error_message or 'model not found' in error_message:
                print("✅ 記憶體已清空")
                print("   沒有預載入的模型，Auto-Evict 可以正常工作")
                return True
            else:
                print(f"⚠️  未知狀態: {error_message}")
                return False
                
        elif response.status_code == 200:
            result = response.json()
            model = result.get('model', 'Unknown')
            print("❌ 記憶體未清空")
            print(f"   檢測到預載入模型: {model}")
            print("   請在 LM Studio 中手動卸載此模型")
            return False
            
        else:
            print(f"❌ 連接錯誤: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到 LM Studio")
        print("   請確認 LM Studio 正在運行並且 Server 已啟動")
        return False
    except Exception as e:
        print(f"❌ 測試錯誤: {e}")
        return False


if __name__ == "__main__":
    if verify_clean_memory():
        print("\n🎉 記憶體清空成功！")
        print("現在可以執行: make test-auto-evict")
    else:
        print("\n💡 請執行以下步驟:")
        print("1. 在 LM Studio 中手動卸載所有載入的模型")
        print("2. 或完全重啟 LM Studio 應用程式")
        print("3. 重新執行此驗證腳本")