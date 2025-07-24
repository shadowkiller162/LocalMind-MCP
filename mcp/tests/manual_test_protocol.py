#!/usr/bin/env python3
"""
MCP 協議處理器手動測試腳本

使用方法:
docker compose exec django python mcp/tests/manual_test_protocol.py
"""

import asyncio
import json
import sys
from mcp.protocol.handler import MCPHandler
from mcp.protocol.types import MCPConnectionState


async def test_basic_protocol():
    """測試基本協議功能"""
    print("=== 測試基本協議功能 ===")
    
    handler = MCPHandler()
    
    # 1. 測試 ping 請求
    print("1. 測試 ping 請求...")
    ping_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "ping",
        "params": {}
    }
    
    response = await handler.handle_message(json.dumps(ping_request))
    print(f"   請求: {ping_request['method']}")
    print(f"   回應: {response}")
    
    # 驗證回應格式
    try:
        response_data = json.loads(response)
        if response_data.get("result", {}).get("pong") is True:
            print("   ✅ ping 測試通過")
        else:
            print("   ❌ ping 回應格式錯誤")
            return False
    except Exception as e:
        print(f"   ❌ ping 回應解析失敗: {e}")
        return False
    
    return True


async def test_initialization_flow():
    """測試初始化流程"""
    print("\n=== 測試初始化流程 ===")
    
    handler = MCPHandler()
    
    # 檢查初始狀態
    initial_state = handler.get_state()
    print(f"初始連接狀態: {initial_state.value}")
    
    if initial_state != MCPConnectionState.DISCONNECTED:
        print("❌ 初始狀態應該是 DISCONNECTED")
        return False
    
    # 1. 發送初始化請求
    print("\n1. 發送初始化請求...")
    init_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "initialize",
        "params": {
            "protocolVersion": "1.0",
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            },
            "capabilities": {
                "experimental": {},
                "logging": {},
                "prompts": {},
                "resources": {},
                "tools": {}
            }
        }
    }
    
    response = await handler.handle_message(json.dumps(init_request))
    print(f"   初始化請求已發送")
    
    # 檢查連接狀態
    connecting_state = handler.get_state()
    print(f"   初始化後狀態: {connecting_state.value}")
    
    if connecting_state != MCPConnectionState.CONNECTING:
        print("   ❌ 初始化後狀態應該是 CONNECTING")
        return False
    
    # 驗證初始化回應
    try:
        response_data = json.loads(response)
        server_info = response_data.get("result", {})
        
        print(f"   協議版本: {server_info.get('protocolVersion')}")
        print(f"   伺服器名稱: {server_info.get('serverInfo', {}).get('name')}")
        print(f"   伺服器版本: {server_info.get('serverInfo', {}).get('version')}")
        
        if server_info.get("protocolVersion") == "1.0":
            print("   ✅ 初始化回應正確")
        else:
            print("   ❌ 初始化回應格式錯誤")
            return False
    except Exception as e:
        print(f"   ❌ 初始化回應解析失敗: {e}")
        return False
    
    # 2. 發送初始化完成通知
    print("\n2. 發送初始化完成通知...")
    initialized_notification = {
        "jsonrpc": "2.0",
        "method": "initialized",
        "params": {}
    }
    
    response = await handler.handle_message(json.dumps(initialized_notification))
    print(f"   初始化完成通知已發送")
    print(f"   通知回應: {response}")  # 應該是 None
    
    # 檢查最終連接狀態
    connected_state = handler.get_state()
    print(f"   最終狀態: {connected_state.value}")
    
    if connected_state != MCPConnectionState.CONNECTED:
        print("   ❌ 最終狀態應該是 CONNECTED")
        return False
    
    print("   ✅ 初始化流程完成")
    return True


async def test_error_handling():
    """測試錯誤處理"""
    print("\n=== 測試錯誤處理 ===")
    
    handler = MCPHandler()
    
    # 1. 測試無效 JSON
    print("1. 測試無效 JSON...")
    invalid_json = "{ invalid json }"
    
    response = await handler.handle_message(invalid_json)
    print(f"   無效 JSON: {invalid_json}")
    print(f"   錯誤回應: {response}")
    
    try:
        error_response = json.loads(response)
        if error_response.get("error", {}).get("code") == -32700:
            print("   ✅ JSON 解析錯誤處理正確")
        else:
            print("   ❌ JSON 解析錯誤代碼不正確")
            return False
    except Exception as e:
        print(f"   ❌ 錯誤回應解析失敗: {e}")
        return False
    
    # 2. 測試無效方法
    print("\n2. 測試無效方法...")
    invalid_method_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "unknown_method",
        "params": {}
    }
    
    response = await handler.handle_message(json.dumps(invalid_method_request))
    print(f"   無效方法請求: {invalid_method_request['method']}")
    
    try:
        error_response = json.loads(response)
        if error_response.get("error", {}).get("code") == -32601:
            print("   ✅ 方法未找到錯誤處理正確")
        else:
            print("   ❌ 方法未找到錯誤代碼不正確")
            return False
    except Exception as e:
        print(f"   ❌ 錯誤回應解析失敗: {e}")
        return False
    
    # 3. 測試無效協議版本
    print("\n3. 測試無效協議版本...")
    invalid_version_request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "initialize",
        "params": {
            "protocolVersion": "999.0",  # 不支援的版本
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    response = await handler.handle_message(json.dumps(invalid_version_request))
    print(f"   無效協議版本: 999.0")
    
    try:
        error_response = json.loads(response)
        if "error" in error_response:
            print("   ✅ 協議版本錯誤處理正確")
        else:
            print("   ❌ 協議版本錯誤未正確處理")
            return False
    except Exception as e:
        print(f"   ❌ 錯誤回應解析失敗: {e}")
        return False
    
    return True


async def test_shutdown_flow():
    """測試關閉流程"""
    print("\n=== 測試關閉流程 ===")
    
    handler = MCPHandler()
    
    # 先完成初始化
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "1.0",
            "clientInfo": {"name": "test", "version": "1.0"}
        }
    }
    
    await handler.handle_message(json.dumps(init_request))
    
    initialized_notification = {
        "jsonrpc": "2.0",
        "method": "initialized",
        "params": {}
    }
    
    await handler.handle_message(json.dumps(initialized_notification))
    
    # 確認已連接
    if handler.get_state() != MCPConnectionState.CONNECTED:
        print("❌ 初始化失敗，無法測試關閉流程")
        return False
    
    print("初始狀態: CONNECTED")
    
    # 發送關閉請求
    shutdown_request = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "shutdown",
        "params": {}
    }
    
    response = await handler.handle_message(json.dumps(shutdown_request))
    print("關閉請求已發送")
    
    # 檢查狀態
    final_state = handler.get_state()
    print(f"關閉後狀態: {final_state.value}")
    
    if final_state != MCPConnectionState.DISCONNECTED:
        print("❌ 關閉後狀態應該是 DISCONNECTED")
        return False
    
    # 驗證關閉回應
    try:
        response_data = json.loads(response)
        if "result" in response_data:
            print("✅ 關閉流程正確")
            return True
        else:
            print("❌ 關閉回應格式錯誤")
            return False
    except Exception as e:
        print(f"❌ 關閉回應解析失敗: {e}")
        return False


async def test_message_formats():
    """測試各種訊息格式"""
    print("\n=== 測試訊息格式 ===")
    
    handler = MCPHandler()
    
    # 1. 測試請求訊息格式
    print("1. 測試請求訊息格式...")
    request_tests = [
        {
            "name": "標準請求",
            "message": {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "ping",
                "params": {}
            },
            "should_succeed": True
        },
        {
            "name": "無參數請求",
            "message": {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "ping"
            },
            "should_succeed": True
        },
        {
            "name": "缺少 jsonrpc",
            "message": {
                "id": 3,
                "method": "ping",
                "params": {}
            },
            "should_succeed": False
        },
        {
            "name": "錯誤 jsonrpc 版本",
            "message": {
                "jsonrpc": "1.0",
                "id": 4,
                "method": "ping",
                "params": {}
            },
            "should_succeed": False
        }
    ]
    
    for test in request_tests:
        try:
            response = await handler.handle_message(json.dumps(test["message"]))
            response_data = json.loads(response)
            
            has_error = "error" in response_data
            success = not has_error if test["should_succeed"] else has_error
            
            status = "✅" if success else "❌"
            print(f"   {status} {test['name']}: {'通過' if success else '失敗'}")
            
            if not success:
                return False
                
        except Exception as e:
            print(f"   ❌ {test['name']} 測試異常: {e}")
            return False
    
    # 2. 測試通知訊息格式
    print("\n2. 測試通知訊息格式...")
    notification_tests = [
        {
            "name": "標準通知",
            "message": {
                "jsonrpc": "2.0",
                "method": "initialized",
                "params": {}
            },
            "should_succeed": True
        },
        {
            "name": "無參數通知",
            "message": {
                "jsonrpc": "2.0",
                "method": "initialized"
            },
            "should_succeed": True
        }
    ]
    
    for test in notification_tests:
        try:
            response = await handler.handle_message(json.dumps(test["message"]))
            
            # 通知應該返回 None（無回應）
            success = response is None if test["should_succeed"] else response is not None
            
            status = "✅" if success else "❌"
            print(f"   {status} {test['name']}: {'通過' if success else '失敗'}")
            
            if not success:
                return False
                
        except Exception as e:
            print(f"   ❌ {test['name']} 測試異常: {e}")
            return False
    
    return True


async def main():
    """主測試函數"""
    print("🚀 開始 MCP 協議處理器手動測試")
    print("=" * 50)
    
    tests = [
        ("基本協議功能", test_basic_protocol),
        ("初始化流程", test_initialization_flow),
        ("錯誤處理", test_error_handling),
        ("關閉流程", test_shutdown_flow),
        ("訊息格式", test_message_formats),
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
    
    print("\n" + "=" * 50)
    print(f"🏁 測試完成: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有協議測試通過！")
        return True
    else:
        print("⚠️  部分協議測試失敗")
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