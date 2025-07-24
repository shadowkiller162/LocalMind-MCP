#!/usr/bin/env python3
"""
Ollama 客戶端手動測試腳本

此腳本需要 Ollama 服務正在運行才能執行完整測試。
如果 Ollama 未運行，部分測試會失敗，這是正常現象。

使用方法:
docker compose exec django python mcp/tests/manual_test_ollama.py
"""

import asyncio
import sys
from mcp.llm.client import OllamaClient
from mcp.llm.manager import ModelManager
from mcp.llm.types import ChatMessage, GenerateRequest, ChatRequest


async def test_ollama_client_manual():
    """測試 Ollama 客戶端基本功能"""
    print("=== Ollama 客戶端手動測試 ===")
    
    client = OllamaClient()
    
    # 1. 測試健康檢查
    print("1. 測試 Ollama 服務健康檢查...")
    try:
        health = await client.health_check()
        print(f"   健康檢查結果: {'✅ 正常' if health else '❌ 異常'}")
        
        if not health:
            print("   ⚠️  Ollama 服務未運行，跳過後續測試")
            return False
    except Exception as e:
        print(f"   ❌ 健康檢查失敗: {e}")
        print("   ⚠️  請確保 Ollama 服務正在運行")
        return False
    
    # 2. 測試模型列表
    print("\n2. 測試模型列表...")
    try:
        async with client:
            models = await client.list_models()
            print(f"   找到 {len(models)} 個模型:")
            for model in models[:3]:  # 只顯示前3個
                print(f"     - {model.name} (大小: {model.size} bytes)")
    except Exception as e:
        print(f"   ❌ 獲取模型列表失敗: {e}")
    
    # 3. 測試文本生成（需要模型）
    print("\n3. 測試文本生成...")
    try:
        async with client:
            # 嘗試使用常見的小模型
            test_models = ["llama2", "llama3.2", "qwen2", "phi3"]
            
            for model_name in test_models:
                try:
                    print(f"   嘗試模型: {model_name}")
                    request = GenerateRequest(
                        model=model_name,
                        prompt="Hello, how are you? Please respond in one sentence.",
                    )
                    
                    response = await client.generate(request)
                    print(f"   ✅ 生成成功:")
                    print(f"     模型: {response.model}")
                    print(f"     回應: {response.content[:100]}...")
                    break
                except Exception as e:
                    print(f"   ❌ 模型 {model_name} 生成失敗: {e}")
                    continue
            else:
                print("   ⚠️  沒有可用的模型進行測試")
    except Exception as e:
        print(f"   ❌ 文本生成測試失敗: {e}")
    
    return True


async def test_model_manager_manual():
    """測試模型管理器功能"""
    print("\n=== 模型管理器手動測試 ===")
    
    manager = ModelManager()
    
    # 1. 測試初始化
    print("1. 測試管理器初始化...")
    try:
        await manager.initialize()
        print("   ✅ 初始化成功")
    except Exception as e:
        print(f"   ❌ 初始化失敗: {e}")
        return False
    
    # 2. 測試健康檢查
    print("\n2. 測試管理器健康檢查...")
    try:
        health = await manager.health_check()
        print(f"   健康檢查結果: {'✅ 正常' if health else '❌ 異常'}")
    except Exception as e:
        print(f"   ❌ 健康檢查失敗: {e}")
    
    # 3. 測試模型列表
    print("\n3. 測試模型列表...")
    try:
        models = await manager.list_models()
        print(f"   管理器中有 {len(models)} 個模型")
        
        if models:
            print("   前3個模型:")
            for model in models[:3]:
                print(f"     - {model.name} (狀態: {model.status.value})")
    except Exception as e:
        print(f"   ❌ 獲取模型列表失敗: {e}")
    
    # 4. 測試預設模型
    print("\n4. 測試預設模型...")
    try:
        default_model = await manager.get_default_model()
        print(f"   預設模型: {default_model}")
    except Exception as e:
        print(f"   ❌ 獲取預設模型失敗: {e}")
    
    # 5. 測試聊天功能（如果有可用模型）
    print("\n5. 測試聊天功能...")
    try:
        models = await manager.list_models()
        if models:
            test_model = models[0].name
            messages = [
                ChatMessage(role="user", content="Hello! Please say hi back in one word.")
            ]
            
            response = await manager.chat(test_model, messages)
            print(f"   ✅ 聊天成功:")
            print(f"     模型: {response.model}")
            print(f"     回應: {response.content}")
        else:
            print("   ⚠️  沒有可用模型進行聊天測試")
    except Exception as e:
        print(f"   ❌ 聊天測試失敗: {e}")
    
    # 6. 清理
    print("\n6. 清理管理器...")
    try:
        await manager.cleanup()
        print("   ✅ 清理成功")
    except Exception as e:
        print(f"   ❌ 清理失敗: {e}")
    
    return True


async def main():
    """主測試函數"""
    print("🚀 開始 MCP Ollama 整合手動測試")
    print("=" * 50)
    
    # 測試 Ollama 客戶端
    client_success = await test_ollama_client_manual()
    
    if client_success:
        # 測試模型管理器
        await test_model_manager_manual()
    
    print("\n" + "=" * 50)
    print("🏁 測試完成")
    
    if not client_success:
        print("\n💡 如要完整測試，請確保:")
        print("   1. Ollama 服務正在運行 (ollama serve)")
        print("   2. 至少安裝一個模型 (ollama pull llama2)")
        print("   3. 網路連接正常")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  測試被用戶中斷")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 測試執行失敗: {e}")
        sys.exit(1)