#!/usr/bin/env python3
"""
LM Studio 整合手動測試腳本

測試 LM Studio 與 MCP 系統的整合功能。
此腳本需要 LM Studio 正在運行並載入了模型才能執行完整測試。

使用方法:
docker compose exec django python -m mcp.tests.manual_test_lmstudio

前置條件:
1. LM Studio 0.3.20 已安裝並運行
2. 已載入 DeepSeek-R1-Distill-Qwen-7B 或其他模型
3. LM Studio 的 Local Server 已啟動 (通常在 http://localhost:1234)
"""

import asyncio
import sys
from mcp.llm.lmstudio_client import LMStudioClient
from mcp.llm.unified_manager import UnifiedModelManager, LLMServiceType
from mcp.llm.types import ChatMessage


async def test_lmstudio_client():
    """測試 LM Studio 客戶端基本功能"""
    print("=== LM Studio 客戶端測試 ===")
    
    client = LMStudioClient()
    
    # 1. 測試健康檢查
    print("1. 測試 LM Studio 服務健康檢查...")
    try:
        health = await client.health_check()
        print(f"   健康檢查結果: {'✅ 正常' if health else '❌ 異常'}")
        
        if not health:
            print("   ⚠️  LM Studio 服務未運行，跳過後續測試")
            print("   💡 請確保:")
            print("      1. LM Studio 應用程式已啟動")
            print("      2. 至少載入一個模型")
            print("      3. 'Local Server' 已啟動 (預設端口 1234)")
            return False
    except Exception as e:
        print(f"   ❌ 健康檢查失敗: {e}")
        print("   ⚠️  請確保 LM Studio 的 Local Server 正在運行")
        return False
    
    # 2. 測試模型列表
    print("\n2. 測試模型列表...")
    try:
        async with client:
            models = await client.list_models()
            print(f"   找到 {len(models)} 個模型:")
            
            deepseek_found = False
            for i, model in enumerate(models):
                print(f"     {i+1}. {model.name}")
                if model.details:
                    print(f"        擁有者: {model.details.get('owned_by', 'unknown')}")
                    print(f"        物件類型: {model.details.get('object', 'unknown')}")
                
                # 檢查是否有 DeepSeek 模型
                if "deepseek" in model.name.lower():
                    deepseek_found = True
                    print(f"        🎯 發現 DeepSeek 模型！")
            
            if deepseek_found:
                print("   ✅ 找到 DeepSeek 模型")
            else:
                print("   ⚠️  未找到 DeepSeek 模型，但有其他可用模型")
                
    except Exception as e:
        print(f"   ❌ 獲取模型列表失敗: {e}")
        return False
    
    # 3. 測試文本生成
    print("\n3. 測試文本生成...")
    try:
        async with client:
            models = await client.list_models()
            if not models:
                print("   ⚠️  沒有可用模型進行測試")
                return False
            
            test_model = models[0].name
            print(f"   使用模型: {test_model}")
            
            from mcp.llm.types import GenerateRequest
            request = GenerateRequest(
                model=test_model,
                prompt="Hello! Please introduce yourself in one sentence.",
            )
            
            print("   發送請求...")
            response = await client.generate(request)
            
            print(f"   ✅ 生成成功:")
            print(f"     模型: {response.model}")
            print(f"     回應: {response.content[:200]}...")
            print(f"     完成狀態: {'已完成' if response.done else '進行中'}")
            
            if response.prompt_eval_count:
                print(f"     提示 Token 數: {response.prompt_eval_count}")
            if response.eval_count:
                print(f"     生成 Token 數: {response.eval_count}")
                
    except Exception as e:
        print(f"   ❌ 文本生成失敗: {e}")
        return False
    
    # 4. 測試聊天功能
    print("\n4. 測試聊天功能...")
    try:
        async with client:
            models = await client.list_models()
            test_model = models[0].name
            
            messages = [
                ChatMessage(role="system", content="You are a helpful AI assistant."),
                ChatMessage(role="user", content="What is the capital of Taiwan? Answer in one sentence.")
            ]
            
            from mcp.llm.types import ChatRequest
            request = ChatRequest(
                model=test_model,
                messages=messages
            )
            
            print(f"   使用模型: {test_model}")
            print("   發送聊天請求...")
            
            response = await client.chat(request)
            
            print(f"   ✅ 聊天成功:")
            print(f"     模型: {response.model}")
            print(f"     回應: {response.content}")
            
    except Exception as e:
        print(f"   ❌ 聊天功能測試失敗: {e}")
        return False
    
    return True


async def test_unified_manager():
    """測試統一模型管理器"""
    print("\n=== 統一模型管理器測試 ===")
    
    # 測試自動檢測服務
    manager = UnifiedModelManager(preferred_service=LLMServiceType.AUTO)
    
    # 1. 測試初始化
    print("1. 測試管理器初始化...")
    try:
        await manager.initialize()
        print("   ✅ 初始化成功")
    except Exception as e:
        print(f"   ❌ 初始化失敗: {e}")
        return False
    
    # 2. 測試服務可用性檢查
    print("\n2. 測試服務可用性...")
    try:
        services = await manager.get_available_services()
        print("   可用服務:")
        for service, available in services.items():
            status = "✅ 可用" if available else "❌ 不可用"
            print(f"     {service}: {status}")
        
        available_count = sum(1 for available in services.values() if available)
        if available_count > 0:
            print(f"   ✅ 找到 {available_count} 個可用服務")
        else:
            print("   ⚠️  沒有可用的 LLM 服務")
            return False
            
    except Exception as e:
        print(f"   ❌ 服務檢查失敗: {e}")
        return False
    
    # 3. 測試模型列表
    print("\n3. 測試統一模型列表...")
    try:
        models = await manager.list_models()
        print(f"   找到 {len(models)} 個模型:")
        
        ollama_count = 0
        lmstudio_count = 0
        
        for model in models[:5]:  # 只顯示前5個
            print(f"     - {model.name}")
            if "ollama:" in model.name:
                ollama_count += 1
            elif "lmstudio:" in model.name:
                lmstudio_count += 1
        
        print(f"   服務分布:")
        print(f"     Ollama: {ollama_count} 個模型")
        print(f"     LM Studio: {lmstudio_count} 個模型")
        
    except Exception as e:
        print(f"   ❌ 模型列表獲取失敗: {e}")
        return False
    
    # 4. 測試推薦模型
    print("\n4. 測試推薦模型...")
    try:
        recommended = await manager.get_recommended_model()
        if recommended:
            print(f"   推薦模型: {recommended}")
            
            # 測試推薦模型是否包含 DeepSeek
            if "deepseek" in recommended.lower():
                print("   🎯 推薦的是 DeepSeek 模型！")
            elif "lmstudio" in recommended:
                print("   ✅ 推薦的是 LM Studio 模型")
            else:
                print("   ✅ 找到推薦模型")
        else:
            print("   ⚠️  沒有可推薦的模型")
            
    except Exception as e:
        print(f"   ❌ 推薦模型獲取失敗: {e}")
        return False
    
    # 5. 測試使用推薦模型進行對話
    print("\n5. 測試推薦模型對話...")
    try:
        recommended = await manager.get_recommended_model()
        if recommended:
            messages = [
                ChatMessage(role="user", content="你好！請用一句話自我介紹。")
            ]
            
            print(f"   使用模型: {recommended}")
            response = await manager.chat(recommended, messages)
            
            print(f"   ✅ 對話成功:")
            print(f"     回應: {response.content[:150]}...")
        else:
            print("   ⚠️  沒有可用模型進行測試")
            
    except Exception as e:
        print(f"   ❌ 對話測試失敗: {e}")
        return False
    
    # 6. 測試健康檢查
    print("\n6. 測試健康檢查...")
    try:
        health_status = await manager.health_check()
        print("   健康檢查結果:")
        for service, healthy in health_status.items():
            status = "✅ 健康" if healthy else "❌ 異常"
            print(f"     {service}: {status}")
            
    except Exception as e:
        print(f"   ❌ 健康檢查失敗: {e}")
        return False
    
    # 7. 清理
    await manager.cleanup()
    print("   ✅ 管理器清理完成")
    
    return True


async def test_deepseek_specific():
    """專門測試 DeepSeek 模型功能"""
    print("\n=== DeepSeek 模型專門測試 ===")
    
    manager = UnifiedModelManager(preferred_service=LLMServiceType.AUTO)
    
    try:
        await manager.initialize()
        
        # 查找 DeepSeek 模型
        models = await manager.list_models()
        deepseek_models = [
            model for model in models 
            if "deepseek" in model.name.lower()
        ]
        
        if not deepseek_models:
            print("   ⚠️  未找到 DeepSeek 模型")
            print("   💡 請確保在 LM Studio 中載入了 DeepSeek-R1-Distill-Qwen-7B 模型")
            return False
        
        print(f"   找到 {len(deepseek_models)} 個 DeepSeek 模型:")
        for model in deepseek_models:
            print(f"     - {model.name}")
        
        # 使用第一個 DeepSeek 模型進行測試
        test_model = deepseek_models[0].name
        print(f"\n   使用模型進行深度測試: {test_model}")
        
        # 測試中文對話
        print("\n   測試中文對話能力...")
        messages = [
            ChatMessage(role="user", content="請用繁體中文介紹一下台灣的美食文化，大約50字。")
        ]
        
        response = await manager.chat(test_model, messages)
        print(f"   中文回應: {response.content}")
        
        # 測試程式碼生成
        print("\n   測試程式碼生成能力...")
        messages = [
            ChatMessage(role="user", content="請寫一個 Python 函數來計算斐波那契數列的第 n 項，並提供簡單的測試。")
        ]
        
        response = await manager.chat(test_model, messages)
        print(f"   程式碼回應: {response.content[:300]}...")
        
        # 測試邏輯推理
        print("\n   測試邏輯推理能力...")
        messages = [
            ChatMessage(role="user", content="如果今天是星期三，那麼三天後是星期幾？請解釋你的推理過程。")
        ]
        
        response = await manager.chat(test_model, messages)
        print(f"   推理回應: {response.content}")
        
        print("   ✅ DeepSeek 模型功能測試完成")
        
        await manager.cleanup()
        return True
        
    except Exception as e:
        print(f"   ❌ DeepSeek 測試失敗: {e}")
        return False


async def main():
    """主測試函數"""
    print("🚀 開始 LM Studio 整合手動測試")
    print("=" * 60)
    
    print("📋 測試環境檢查:")
    print("   - LM Studio 版本: 0.3.20")
    print("   - 預期模型: DeepSeek-R1-Distill-Qwen-7B-GGUF")
    print("   - 預期端口: http://localhost:1234")
    
    tests = [
        ("LM Studio 客戶端", test_lmstudio_client),
        ("統一模型管理器", test_unified_manager),
        ("DeepSeek 模型專門測試", test_deepseek_specific),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 執行測試: {test_name}")
        try:
            if await test_func():
                passed += 1
                print(f"✅ {test_name} 測試通過")
            else:
                print(f"❌ {test_name} 測試失敗")
        except Exception as e:
            print(f"❌ {test_name} 測試異常: {e}")
    
    print("\n" + "=" * 60)
    print(f"🏁 測試完成: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有 LM Studio 整合測試通過！")
        print("\n💡 您的 DeepSeek 模型已準備就緒，可以:")
        print("   1. 整合到 MCP 伺服器中")
        print("   2. 在 Django 後端中使用")
        print("   3. 提供給前端應用程式呼叫")
        return True
    else:
        print("⚠️  部分測試失敗")
        print("\n🔧 修復建議:")
        print("   1. 確保 LM Studio 應用程式正在運行")
        print("   2. 確保至少載入一個模型")
        print("   3. 確保 'Local Server' 已啟動")
        print("   4. 檢查端口 1234 是否被其他程式占用")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  測試被用戶中斷")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 測試執行失敗: {e}")
        sys.exit(1)