#!/usr/bin/env python3
"""
MCP-LMStudio 開發環境測試

針對本地開發環境優化的測試腳本，使用適合 DeepSeek R1 模型的超時設定
"""

import asyncio
import sys
import os
from pathlib import Path

# 載入開發環境變數
def load_dev_env():
    """載入開發環境配置"""
    env_file = Path(__file__).parent.parent.parent / '.env.mcp.dev'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print(f"✅ 載入開發環境配置: {env_file}")
    else:
        print(f"⚠️  未找到開發環境配置檔案: {env_file}")

# 載入環境配置
load_dev_env()

from mcp.llm.unified_manager import UnifiedModelManager, LLMServiceType
from mcp.llm.types import ChatMessage


async def dev_test():
    """開發環境測試"""
    print("🔧 MCP-LMStudio 開發環境測試")
    print("=" * 50)
    
    manager = UnifiedModelManager(preferred_service=LLMServiceType.LMSTUDIO)
    
    try:
        # 1. 初始化（使用開發環境配置）
        print("1. 初始化管理器（開發環境配置）...")
        await manager.initialize()
        print("   ✅ 成功")
        
        # 2. 檢查服務狀態
        print("\n2. 檢查 LM Studio 服務狀態...")
        health = await manager.health_check()
        lmstudio_ok = health.get('lmstudio', False)
        print(f"   LM Studio: {'✅ 正常' if lmstudio_ok else '❌ 異常'}")
        
        if not lmstudio_ok:
            print("   請確保 LM Studio Local Server 正在運行")
            return False
        
        # 3. 獲取 DeepSeek 模型
        print("\n3. 尋找 DeepSeek 模型...")
        models = await manager.list_models()
        deepseek_models = [m for m in models if 'deepseek' in m.name.lower()]
        
        if not deepseek_models:
            print("   ❌ 未找到 DeepSeek 模型")
            return False
        
        test_model = deepseek_models[0].name
        print(f"   ✅ 找到模型: {test_model}")
        
        # 4. 簡單對話測試（適應較長等待時間）
        print(f"\n4. 測試對話（模型: {test_model}）...")
        print("   ⏳ 等待模型回應（可能需要較長時間）...")
        
        messages = [
            ChatMessage(
                role="user", 
                content="請用一句話介紹你自己，並說明你是在哪個平台上運行的。"
            )
        ]
        
        response = await manager.chat(test_model, messages)
        
        print(f"   ✅ 對話成功！")
        print(f"   📝 模型回應: {response.content[:200]}...")
        
        if response.eval_count:
            print(f"   📊 生成 Token 數: {response.eval_count}")
        
        # 5. 測試程式碼生成
        print(f"\n5. 測試程式碼生成能力...")
        print("   ⏳ 生成 Python 函數...")
        
        code_messages = [
            ChatMessage(
                role="user",
                content="請寫一個 Python 函數來計算兩個數字的最大公約數（GCD），使用歐幾里得算法。"
            )
        ]
        
        code_response = await manager.chat(test_model, code_messages)
        print(f"   ✅ 程式碼生成成功！")
        print(f"   📝 生成的程式碼（前200字）: {code_response.content[:200]}...")
        
        print(f"\n🎉 開發環境測試完成！")
        print(f"✅ MCP 系統已成功整合 LM Studio DeepSeek 模型")
        print(f"✅ 超時設定已優化，適合本地開發使用")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        print(f"💡 建議:")
        print(f"   1. 確認 LM Studio Local Server 正在運行")
        print(f"   2. 確認 DeepSeek 模型已載入")
        print(f"   3. 檢查網絡連接")
        return False
        
    finally:
        await manager.cleanup()


if __name__ == "__main__":
    print("🚀 啟動開發環境測試...")
    success = asyncio.run(dev_test())
    
    if success:
        print("\n✅ 開發環境配置完成，可以開始使用 MCP 系統！")
    else:
        print("\n❌ 開發環境配置失敗，請檢查設定。")
    
    sys.exit(0 if success else 1)