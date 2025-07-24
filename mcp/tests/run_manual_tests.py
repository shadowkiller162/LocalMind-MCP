#!/usr/bin/env python3
"""
MCP 手動測試執行腳本

統一執行所有 MCP 核心功能的手動測試案例

使用方法:
docker compose exec django python mcp/tests/run_manual_tests.py

或執行特定測試:
docker compose exec django python mcp/tests/run_manual_tests.py --test config
docker compose exec django python mcp/tests/run_manual_tests.py --test protocol
docker compose exec django python mcp/tests/run_manual_tests.py --test connectors
docker compose exec django python mcp/tests/run_manual_tests.py --test ollama
"""

import argparse
import asyncio
import sys
import subprocess
from pathlib import Path


def run_test_script(script_name: str, description: str) -> bool:
    """執行測試腳本"""
    print(f"\n{'='*60}")
    print(f"🧪 執行測試: {description}")
    print(f"📜 腳本: {script_name}")
    print(f"{'='*60}")
    
    try:
        # 執行測試腳本
        result = subprocess.run([
            sys.executable, 
            str(Path(__file__).parent / script_name)
        ], capture_output=False, text=True)
        
        if result.returncode == 0:
            print(f"\n✅ {description} 測試完成")
            return True
        else:
            print(f"\n❌ {description} 測試失敗 (退出碼: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"\n❌ {description} 測試異常: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="MCP 手動測試執行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
可用的測試類型:
  config      - 配置管理系統測試
  protocol    - MCP 協議處理器測試  
  connectors  - 連接器系統測試
  ollama      - Ollama LLM 整合測試
  all         - 執行所有測試 (預設)

範例:
  python run_manual_tests.py                    # 執行所有測試
  python run_manual_tests.py --test config     # 只執行配置測試
  python run_manual_tests.py --test ollama     # 只執行 Ollama 測試
        """
    )
    
    parser.add_argument(
        "--test", "-t",
        choices=["config", "protocol", "connectors", "ollama", "all"],
        default="all",
        help="指定要執行的測試類型 (預設: all)"
    )
    
    parser.add_argument(
        "--continue-on-error", "-c",
        action="store_true",
        help="測試失敗時繼續執行其他測試"
    )
    
    args = parser.parse_args()
    
    # 定義測試配置
    test_configs = {
        "config": {
            "script": "manual_test_config.py",
            "description": "MCP 配置管理系統",
            "priority": 1
        },
        "protocol": {
            "script": "manual_test_protocol.py", 
            "description": "MCP 協議處理器",
            "priority": 2
        },
        "connectors": {
            "script": "manual_test_connectors.py",
            "description": "MCP 連接器系統",
            "priority": 3
        },
        "ollama": {
            "script": "manual_test_ollama.py",
            "description": "Ollama LLM 整合",
            "priority": 4
        }
    }
    
    # 確定要執行的測試
    if args.test == "all":
        tests_to_run = sorted(test_configs.items(), key=lambda x: x[1]["priority"])
    else:
        tests_to_run = [(args.test, test_configs[args.test])]
    
    print("🚀 LocalMind-MCP 手動測試執行器")
    print(f"📋 將執行 {len(tests_to_run)} 個測試:")
    
    for test_name, config in tests_to_run:
        print(f"   - {test_name}: {config['description']}")
    
    print(f"\n⚙️  配置:")
    print(f"   - 失敗時繼續: {'是' if args.continue_on_error else '否'}")
    
    # 執行測試
    results = {}
    
    for test_name, config in tests_to_run:
        success = run_test_script(config["script"], config["description"])
        results[test_name] = success
        
        if not success and not args.continue_on_error:
            print(f"\n⚠️  測試 '{test_name}' 失敗，停止執行")
            break
    
    # 顯示總結果
    print(f"\n{'='*60}")
    print("📊 測試結果總結")
    print(f"{'='*60}")
    
    passed = 0
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ 通過" if success else "❌ 失敗"
        description = test_configs[test_name]["description"]
        print(f"   {test_name:12} | {status} | {description}")
        if success:
            passed += 1
    
    print(f"\n🏁 整體結果: {passed}/{total} 測試通過")
    
    if passed == total:
        print("🎉 所有測試都通過了！MCP 核心功能正常運作")
        
        print(f"\n💡 下一步建議:")
        print("   1. 開始實作具體的連接器 (檔案系統、GitHub 等)")
        print("   2. 建立 FastAPI MCP Server")
        print("   3. 整合到 Django 後端")
        
        return True
    else:
        failed_tests = [name for name, success in results.items() if not success]
        print(f"⚠️  以下測試失敗: {', '.join(failed_tests)}")
        
        print(f"\n🔧 修復建議:")
        if "ollama" in failed_tests:
            print("   - Ollama 測試失敗: 請確保 Ollama 服務正在運行")
            print("     安裝: https://ollama.ai/")
            print("     啟動: ollama serve")
            print("     拉取模型: ollama pull llama2")
        
        for test_name in failed_tests:
            if test_name in ["config", "protocol", "connectors"]:
                print(f"   - {test_name} 測試失敗: 檢查核心模組實作")
        
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  測試被用戶中斷")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 測試執行器異常: {e}")
        sys.exit(1)