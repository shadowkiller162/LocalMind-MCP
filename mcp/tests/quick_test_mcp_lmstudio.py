#!/usr/bin/env python3
"""
MCP-LMStudio 快速整合測試

快速驗證 MCP 系統與 LM Studio 的基本連接和對話功能
"""

import asyncio
import sys
from mcp.llm.unified_manager import UnifiedModelManager, LLMServiceType
from mcp.llm.types import ChatMessage


async def quick_test():
    """快速測試核心功能"""
    print("🔍 MCP-LMStudio 快速整合測試")
    print("=" * 50)
    
    manager = UnifiedModelManager(preferred_service=LLMServiceType.AUTO)
    
    try:
        # 1. 初始化
        print("1. 初始化管理器...")
        await manager.initialize()
        print("   ✅ 成功")
        
        # 2. 檢查服務
        print("\n2. 檢查可用服務...")
        services = await manager.get_available_services()
        print(f"   LM Studio: {'✅' if services.get('lmstudio') else '❌'}")
        print(f"   Ollama: {'✅' if services.get('ollama') else '❌'}")
        
        if not services.get('lmstudio'):
            print("   ❌ LM Studio 不可用")
            return False
        
        # 3. 獲取推薦模型
        print("\n3. 獲取推薦模型...")
        model = await manager.get_recommended_model()
        print(f"   推薦模型: {model}")
        
        # 4. 簡單對話測試
        print("\n4. 測試對話...")
        messages = [
            ChatMessage(role="user", content="Say 'Hello from MCP!' in response.")
        ]
        
        response = await manager.chat(model, messages)
        print(f"   模型回應: {response.content[:100]}...")
        
        print(f"\n✅ 測試完成！MCP 成功與 LM Studio 整合")
        return True
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        return False
    finally:
        await manager.cleanup()


if __name__ == "__main__":
    success = asyncio.run(quick_test())
    sys.exit(0 if success else 1)