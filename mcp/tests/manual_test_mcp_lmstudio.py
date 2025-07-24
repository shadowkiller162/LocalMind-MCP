#!/usr/bin/env python3
"""
MCP 系統調用 LM Studio 伺服器整合測試

測試透過 MCP 系統呼叫 LM Studio 本地伺服器，與 DeepSeek 模型進行對話。
此測試驗證完整的通訊鏈路：MCP 系統 -> LM Studio 伺服器 -> DeepSeek 模型

使用方法:
python -m mcp.tests.manual_test_mcp_lmstudio

前置條件:
1. LM Studio 0.3.20 已安裝並運行
2. 已載入 DeepSeek-R1-Distill-Qwen-7B 模型
3. LM Studio 的 Local Server 已啟動 (http://localhost:1234)
"""

import asyncio
import sys
import json
from datetime import datetime
from mcp.llm.unified_manager import UnifiedModelManager, LLMServiceType
from mcp.llm.types import ChatMessage


class MCPLMStudioTester:
    """MCP 系統與 LM Studio 整合測試器"""
    
    def __init__(self):
        self.manager = UnifiedModelManager(preferred_service=LLMServiceType.AUTO)
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """記錄測試結果"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ 通過" if success else "❌ 失敗"
        print(f"   {status}: {test_name}")
        if details:
            print(f"      詳細: {details}")
    
    async def test_mcp_initialization(self):
        """測試 MCP 系統初始化"""
        print("1. 測試 MCP 系統初始化...")
        try:
            await self.manager.initialize()
            self.log_test("MCP 系統初始化", True, "統一模型管理器已成功初始化")
            return True
        except Exception as e:
            self.log_test("MCP 系統初始化", False, f"初始化失敗: {e}")
            return False
    
    async def test_lmstudio_connectivity(self):
        """測試 LM Studio 連接性"""
        print("\n2. 測試 LM Studio 伺服器連接...")
        try:
            health_status = await self.manager.health_check()
            lmstudio_healthy = health_status.get("lmstudio", False)
            
            if lmstudio_healthy:
                self.log_test("LM Studio 連接", True, "本地伺服器 (localhost:1234) 正常回應")
                return True
            else:
                self.log_test("LM Studio 連接", False, "無法連接到 localhost:1234")
                return False
        except Exception as e:
            self.log_test("LM Studio 連接", False, f"連接測試失敗: {e}")
            return False
    
    async def test_deepseek_model_detection(self):
        """測試 DeepSeek 模型檢測"""
        print("\n3. 測試 DeepSeek 模型檢測...")
        try:
            models = await self.manager.list_models()
            lmstudio_models = [m for m in models if "lmstudio:" in m.name]
            deepseek_models = [m for m in lmstudio_models if "deepseek" in m.name.lower()]
            
            if deepseek_models:
                model_names = [m.name for m in deepseek_models]
                self.log_test("DeepSeek 模型檢測", True, f"找到模型: {model_names}")
                return deepseek_models[0].name
            else:
                all_lmstudio = [m.name for m in lmstudio_models]
                self.log_test("DeepSeek 模型檢測", False, f"未找到 DeepSeek，可用模型: {all_lmstudio}")
                return lmstudio_models[0].name if lmstudio_models else None
        except Exception as e:
            self.log_test("DeepSeek 模型檢測", False, f"模型檢測失敗: {e}")
            return None
    
    async def test_simple_dialogue(self, model_name: str):
        """測試簡單對話"""
        print("\n4. 測試簡單對話...")
        try:
            messages = [
                ChatMessage(role="user", content="Hello! Please respond with exactly 'MCP-LMStudio connection successful' to confirm the integration works.")
            ]
            
            response = await self.manager.chat(model_name, messages)
            
            if response and response.content:
                success_indicator = "successful" in response.content.lower() or "成功" in response.content
                self.log_test("簡單對話", True, f"模型回應: {response.content[:100]}...")
                return True
            else:
                self.log_test("簡單對話", False, "模型未回應或回應為空")
                return False
        except Exception as e:
            self.log_test("簡單對話", False, f"對話失敗: {e}")
            return False
    
    async def test_chinese_dialogue(self, model_name: str):
        """測試中文對話"""
        print("\n5. 測試中文對話能力...")
        try:
            messages = [
                ChatMessage(role="user", content="你好！請用繁體中文回答：什麼是人工智慧？請用一句話回答。")
            ]
            
            response = await self.manager.chat(model_name, messages)
            
            if response and response.content:
                # 檢查是否包含中文字符
                has_chinese = any('\u4e00' <= char <= '\u9fff' for char in response.content)
                self.log_test("中文對話", has_chinese, f"回應: {response.content}")
                return has_chinese
            else:
                self.log_test("中文對話", False, "無中文回應")
                return False
        except Exception as e:
            self.log_test("中文對話", False, f"中文對話失敗: {e}")
            return False
    
    async def test_code_generation(self, model_name: str):
        """測試程式碼生成"""
        print("\n6. 測試程式碼生成能力...")
        try:
            messages = [
                ChatMessage(role="user", content="Please write a simple Python function to add two numbers. Just the function, no explanation.")
            ]
            
            response = await self.manager.chat(model_name, messages)
            
            if response and response.content:
                has_code = "def " in response.content and "return" in response.content
                self.log_test("程式碼生成", has_code, f"生成代碼包含函數定義: {'是' if has_code else '否'}")
                return has_code
            else:
                self.log_test("程式碼生成", False, "無程式碼回應")
                return False
        except Exception as e:
            self.log_test("程式碼生成", False, f"程式碼生成失敗: {e}")
            return False
    
    async def test_context_memory(self, model_name: str):
        """測試上下文記憶"""
        print("\n7. 測試上下文記憶...")
        try:
            # 第一輪對話
            messages = [
                ChatMessage(role="user", content="My name is Alex. Remember this.")
            ]
            response1 = await self.manager.chat(model_name, messages)
            
            # 第二輪對話，測試是否記住名字
            messages.append(ChatMessage(role="assistant", content=response1.content))
            messages.append(ChatMessage(role="user", content="What is my name?"))
            
            response2 = await self.manager.chat(model_name, messages)
            
            if response2 and response2.content:
                remembers_name = "alex" in response2.content.lower()
                self.log_test("上下文記憶", remembers_name, f"回應: {response2.content}")
                return remembers_name
            else:
                self.log_test("上下文記憶", False, "無回應")
                return False
        except Exception as e:
            self.log_test("上下文記憶", False, f"上下文測試失敗: {e}")
            return False
    
    async def test_performance_metrics(self, model_name: str):
        """測試性能指標"""
        print("\n8. 測試性能指標...")
        try:
            messages = [
                ChatMessage(role="user", content="Count from 1 to 10.")
            ]
            
            start_time = datetime.now()
            response = await self.manager.chat(model_name, messages)
            end_time = datetime.now()
            
            duration = (end_time - start_time).total_seconds()
            
            if response:
                metrics = {
                    "回應時間": f"{duration:.2f} 秒",
                    "回應長度": len(response.content) if response.content else 0,
                    "Token 使用": {
                        "輸入": response.prompt_eval_count or "未知",
                        "輸出": response.eval_count or "未知"
                    }
                }
                self.log_test("性能指標", True, json.dumps(metrics, ensure_ascii=False, indent=2))
                return True
            else:
                self.log_test("性能指標", False, "無性能數據")
                return False
        except Exception as e:
            self.log_test("性能指標", False, f"性能測試失敗: {e}")
            return False
    
    def generate_report(self):
        """生成測試報告"""
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"\n{'='*60}")
        print(f"📊 MCP-LMStudio 整合測試報告")
        print(f"{'='*60}")
        print(f"總測試數: {total}")
        print(f"通過測試: {passed}")
        print(f"失敗測試: {total - passed}")
        print(f"成功率: {(passed/total*100):.1f}%")
        
        if passed == total:
            print(f"\n🎉 所有測試通過！MCP 系統與 LM Studio 整合成功")
            print(f"✅ 您的 DeepSeek 模型可以通過 MCP 系統正常使用")
        else:
            print(f"\n⚠️  {total - passed} 個測試失敗")
            print(f"❌ 需要檢查 MCP 系統與 LM Studio 的整合配置")
        
        print(f"\n📋 詳細結果:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"   {status} {result['test']}")
            if not result["success"] and result["details"]:
                print(f"      📝 {result['details']}")
        
        return passed == total


async def main():
    """主測試函數"""
    print("🚀 開始 MCP 系統調用 LM Studio 整合測試")
    print("="*60)
    
    tester = MCPLMStudioTester()
    
    try:
        # 測試序列
        if not await tester.test_mcp_initialization():
            print("❌ MCP 初始化失敗，無法繼續測試")
            return False
        
        if not await tester.test_lmstudio_connectivity():
            print("❌ LM Studio 連接失敗，請檢查:")
            print("   1. LM Studio 應用程式是否運行")
            print("   2. Local Server 是否已啟動")
            print("   3. 端口 1234 是否可用")
            return False
        
        model_name = await tester.test_deepseek_model_detection()
        if not model_name:
            print("❌ 未找到可用模型，無法繼續測試")
            return False
        
        print(f"\n🎯 使用模型進行完整測試: {model_name}")
        
        # 執行所有對話測試
        await tester.test_simple_dialogue(model_name)
        await tester.test_chinese_dialogue(model_name)
        await tester.test_code_generation(model_name)
        await tester.test_context_memory(model_name)
        await tester.test_performance_metrics(model_name)
        
        # 生成報告
        success = tester.generate_report()
        
        if success:
            print(f"\n💡 下一步建議:")
            print(f"   1. 將 MCP 整合到 Django 後端 API")
            print(f"   2. 建立前端介面調用 DeepSeek 模型")
            print(f"   3. 配置模型參數最佳化")
        
        return success
        
    except KeyboardInterrupt:
        print("\n⚠️  測試被用戶中斷")
        return False
    except Exception as e:
        print(f"\n❌ 測試執行異常: {e}")
        return False
    finally:
        # 清理資源
        try:
            await tester.manager.cleanup()
        except:
            pass


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 程式執行失敗: {e}")
        sys.exit(1)