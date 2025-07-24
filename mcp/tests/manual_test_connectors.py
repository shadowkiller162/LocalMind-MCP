#!/usr/bin/env python3
"""
MCP 連接器系統手動測試腳本

使用方法:
docker compose exec django python mcp/tests/manual_test_connectors.py
"""

import asyncio
import sys
from typing import Dict, Any
from mcp.connectors.base import (
    BaseConnector, ConnectorConfig, ConnectorType, 
    ResourceInfo, ToolInfo
)
from mcp.connectors.registry import registry
from mcp.exceptions import MCPConnectorError


class TestFileSystemConnector(BaseConnector):
    """測試用檔案系統連接器"""
    
    async def initialize(self):
        print(f"   初始化檔案系統連接器: {self.name}")
        
        # 添加測試資源
        self._add_resource(ResourceInfo(
            uri="file:///tmp/test.txt",
            name="test.txt",
            description="測試文字檔案",
            mime_type="text/plain"
        ))
        
        self._add_resource(ResourceInfo(
            uri="file:///tmp/config.json",
            name="config.json", 
            description="配置檔案",
            mime_type="application/json"
        ))
        
        # 添加測試工具
        self._add_tool(ToolInfo(
            name="read_file",
            description="讀取檔案內容",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "檔案路徑"}
                },
                "required": ["path"]
            }
        ))
        
        self._add_tool(ToolInfo(
            name="write_file",
            description="寫入檔案內容",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "檔案路徑"},
                    "content": {"type": "string", "description": "檔案內容"}
                },
                "required": ["path", "content"]
            }
        ))
        
        self._initialized = True
    
    async def cleanup(self):
        print(f"   清理檔案系統連接器: {self.name}")
        self._initialized = False
    
    async def health_check(self):
        return self._initialized
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        if not self._initialized:
            raise MCPConnectorError("Connector not initialized")
        
        print(f"   讀取資源: {uri}")
        
        # 模擬檔案讀取
        if uri == "file:///tmp/test.txt":
            return {
                "uri": uri,
                "contents": [
                    {
                        "type": "text",
                        "text": "這是一個測試文字檔案的內容。"
                    }
                ]
            }
        elif uri == "file:///tmp/config.json":
            return {
                "uri": uri,
                "contents": [
                    {
                        "type": "text",
                        "text": '{"name": "test-config", "version": "1.0"}'
                    }
                ]
            }
        else:
            raise MCPConnectorError(f"Resource not found: {uri}")
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if not self._initialized:
            raise MCPConnectorError("Connector not initialized")
        
        print(f"   呼叫工具: {name} with {arguments}")
        
        if name == "read_file":
            path = arguments.get("path")
            return {
                "content": f"模擬讀取檔案 {path} 的內容",
                "success": True
            }
        elif name == "write_file":
            path = arguments.get("path")
            content = arguments.get("content")
            return {
                "message": f"成功寫入內容到 {path}",
                "bytes_written": len(content),
                "success": True
            }
        else:
            raise MCPConnectorError(f"Unknown tool: {name}")


class TestDatabaseConnector(BaseConnector):
    """測試用資料庫連接器"""
    
    async def initialize(self):
        print(f"   初始化資料庫連接器: {self.name}")
        
        # 添加測試資源
        self._add_resource(ResourceInfo(
            uri="db://localhost/users",
            name="users",
            description="用戶資料表",
            mime_type="application/json"
        ))
        
        # 添加測試工具
        self._add_tool(ToolInfo(
            name="query",
            description="執行資料庫查詢",
            input_schema={
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "SQL 查詢語句"}
                },
                "required": ["sql"]
            }
        ))
        
        self._initialized = True
    
    async def cleanup(self):
        print(f"   清理資料庫連接器: {self.name}")
        self._initialized = False
    
    async def health_check(self):
        return self._initialized
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        if uri == "db://localhost/users":
            return {
                "uri": uri,
                "contents": [
                    {
                        "type": "text",
                        "text": '{"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}'
                    }
                ]
            }
        else:
            raise MCPConnectorError(f"Resource not found: {uri}")
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if name == "query":
            sql = arguments.get("sql")
            return {
                "result": f"模擬執行 SQL: {sql}",
                "rows_affected": 2,
                "success": True
            }
        else:
            raise MCPConnectorError(f"Unknown tool: {name}")


def test_connector_config():
    """測試連接器配置"""
    print("=== 測試連接器配置 ===")
    
    # 1. 測試預設配置
    print("1. 測試預設配置...")
    config = ConnectorConfig(
        name="test-connector",
        type=ConnectorType.FILESYSTEM
    )
    
    print(f"   連接器名稱: {config.name}")
    print(f"   連接器類型: {config.type.value}")
    print(f"   是否啟用: {config.enabled}")
    print(f"   超時時間: {config.timeout}s")
    print(f"   最大重試: {config.max_retries}")
    print(f"   配置項目: {config.config}")
    
    if config.enabled and config.timeout == 30:
        print("   ✅ 預設配置正確")
    else:
        print("   ❌ 預設配置錯誤")
        return False
    
    # 2. 測試自定義配置
    print("\n2. 測試自定義配置...")
    custom_config = ConnectorConfig(
        name="custom-fs",
        type=ConnectorType.FILESYSTEM,
        enabled=True,
        timeout=60,
        max_retries=5,
        config={
            "root_path": "/tmp",
            "read_only": False
        }
    )
    
    print(f"   自定義超時: {custom_config.timeout}s")
    print(f"   自定義重試: {custom_config.max_retries}")
    print(f"   自定義配置: {custom_config.config}")
    
    if custom_config.timeout == 60 and "root_path" in custom_config.config:
        print("   ✅ 自定義配置正確")
    else:
        print("   ❌ 自定義配置錯誤")
        return False
    
    return True


async def test_connector_lifecycle():
    """測試連接器生命週期"""
    print("\n=== 測試連接器生命週期 ===")
    
    # 建立測試連接器
    config = ConnectorConfig(
        name="test-fs",
        type=ConnectorType.FILESYSTEM
    )
    
    connector = TestFileSystemConnector(config)
    
    # 1. 測試初始狀態
    print("1. 測試初始狀態...")
    print(f"   連接器名稱: {connector.name}")
    print(f"   連接器類型: {connector.type.value}")
    print(f"   是否啟用: {connector.is_enabled}")
    print(f"   是否初始化: {connector.is_initialized}")
    
    if not connector.is_initialized:
        print("   ✅ 初始狀態正確")
    else:
        print("   ❌ 初始狀態錯誤")
        return False
    
    # 2. 測試初始化
    print("\n2. 測試初始化...")
    await connector.initialize()
    
    if connector.is_initialized:
        print("   ✅ 初始化成功")
    else:
        print("   ❌ 初始化失敗")
        return False
    
    # 3. 測試健康檢查
    print("\n3. 測試健康檢查...")
    health = await connector.health_check()
    print(f"   健康狀態: {health}")
    
    if health:
        print("   ✅ 健康檢查通過")
    else:
        print("   ❌ 健康檢查失敗")
        return False
    
    # 4. 測試清理
    print("\n4. 測試清理...")
    await connector.cleanup()
    
    if not connector.is_initialized:
        print("   ✅ 清理成功")
    else:
        print("   ❌ 清理失敗")
        return False
    
    return True


async def test_resources_and_tools():
    """測試資源和工具功能"""
    print("\n=== 測試資源和工具功能 ===")
    
    config = ConnectorConfig(
        name="test-fs", 
        type=ConnectorType.FILESYSTEM
    )
    
    async with TestFileSystemConnector(config) as connector:
        # 1. 測試資源列表
        print("1. 測試資源列表...")
        resources = await connector.list_resources()
        print(f"   找到 {len(resources)} 個資源:")
        
        for resource in resources:
            print(f"     - {resource.name} ({resource.uri})")
            print(f"       描述: {resource.description}")
            print(f"       類型: {resource.mime_type}")
        
        if len(resources) >= 2:
            print("   ✅ 資源列表正確")
        else:
            print("   ❌ 資源列表錯誤")
            return False
        
        # 2. 測試資源讀取
        print("\n2. 測試資源讀取...")
        test_uri = "file:///tmp/test.txt"
        
        try:
            resource_content = await connector.read_resource(test_uri)
            print(f"   讀取資源: {test_uri}")
            print(f"   內容: {resource_content}")
            
            if "contents" in resource_content:
                print("   ✅ 資源讀取成功")
            else:
                print("   ❌ 資源內容格式錯誤")
                return False
        except Exception as e:
            print(f"   ❌ 資源讀取失敗: {e}")
            return False
        
        # 3. 測試工具列表
        print("\n3. 測試工具列表...")
        tools = await connector.list_tools()
        print(f"   找到 {len(tools)} 個工具:")
        
        for tool in tools:
            print(f"     - {tool.name}: {tool.description}")
            print(f"       輸入結構: {tool.input_schema}")
        
        if len(tools) >= 2:
            print("   ✅ 工具列表正確")
        else:
            print("   ❌ 工具列表錯誤")
            return False
        
        # 4. 測試工具呼叫
        print("\n4. 測試工具呼叫...")
        
        # 測試讀取檔案工具
        try:
            read_result = await connector.call_tool(
                "read_file", 
                {"path": "/tmp/test.txt"}
            )
            print(f"   讀取檔案結果: {read_result}")
            
            if read_result.get("success"):
                print("   ✅ 讀取檔案工具正常")
            else:
                print("   ❌ 讀取檔案工具失敗")
                return False
        except Exception as e:
            print(f"   ❌ 讀取檔案工具異常: {e}")
            return False
        
        # 測試寫入檔案工具
        try:
            write_result = await connector.call_tool(
                "write_file",
                {"path": "/tmp/output.txt", "content": "Hello World!"}
            )
            print(f"   寫入檔案結果: {write_result}")
            
            if write_result.get("success"):
                print("   ✅ 寫入檔案工具正常")
            else:
                print("   ❌ 寫入檔案工具失敗")
                return False
        except Exception as e:
            print(f"   ❌ 寫入檔案工具異常: {e}")
            return False
    
    return True


async def test_registry():
    """測試連接器註冊表"""
    print("\n=== 測試連接器註冊表 ===")
    
    # 1. 測試連接器註冊
    print("1. 測試連接器註冊...")
    
    # 註冊測試連接器
    registry.register_connector(ConnectorType.FILESYSTEM, TestFileSystemConnector)
    registry.register_connector(ConnectorType.DATABASE, TestDatabaseConnector)
    
    registered_types = registry.list_registered_types()
    print(f"   已註冊類型: {[t.value for t in registered_types]}")
    
    if len(registered_types) >= 2:
        print("   ✅ 連接器註冊成功")
    else:
        print("   ❌ 連接器註冊失敗")
        return False
    
    # 2. 測試連接器建立
    print("\n2. 測試連接器建立...")
    
    # 建立檔案系統連接器
    fs_config = ConnectorConfig(
        name="test-fs",
        type=ConnectorType.FILESYSTEM,
        enabled=True
    )
    
    fs_connector = registry.create_connector(fs_config)
    print(f"   建立檔案系統連接器: {fs_connector}")
    
    if fs_connector.name == "test-fs":
        print("   ✅ 檔案系統連接器建立成功")
    else:
        print("   ❌ 檔案系統連接器建立失敗")
        return False
    
    # 建立資料庫連接器
    db_config = ConnectorConfig(
        name="test-db",
        type=ConnectorType.DATABASE,
        enabled=True
    )
    
    db_connector = registry.create_connector(db_config)
    print(f"   建立資料庫連接器: {db_connector}")
    
    if db_connector.name == "test-db":
        print("   ✅ 資料庫連接器建立成功")
    else:
        print("   ❌ 資料庫連接器建立失敗")
        return False
    
    # 3. 測試註冊表查詢
    print("\n3. 測試註冊表查詢...")
    
    # 查詢單個連接器
    retrieved_fs = registry.get_connector("test-fs")
    if retrieved_fs and retrieved_fs.name == "test-fs":
        print("   ✅ 單個連接器查詢成功")
    else:
        print("   ❌ 單個連接器查詢失敗")
        return False
    
    # 查詢類型連接器
    fs_connectors = registry.get_connectors_by_type(ConnectorType.FILESYSTEM)
    print(f"   檔案系統連接器數量: {len(fs_connectors)}")
    
    # 查詢所有連接器
    all_connectors = registry.list_active_connectors()
    print(f"   總連接器數量: {len(all_connectors)}")
    
    if len(all_connectors) >= 2:
        print("   ✅ 註冊表查詢功能正常")
    else:
        print("   ❌ 註冊表查詢功能異常")
        return False
    
    # 4. 測試批量操作
    print("\n4. 測試批量操作...")
    
    # 批量初始化
    await registry.initialize_all()
    print("   批量初始化完成")
    
    # 批量健康檢查
    health_results = await registry.health_check_all()
    print(f"   健康檢查結果: {health_results}")
    
    healthy_count = sum(1 for healthy in health_results.values() if healthy)
    if healthy_count == len(health_results):
        print("   ✅ 所有連接器健康")
    else:
        print("   ❌ 部分連接器不健康")
        return False
    
    # 批量清理
    await registry.cleanup_all()
    print("   批量清理完成")
    
    return True


async def test_error_scenarios():
    """測試錯誤場景"""
    print("\n=== 測試錯誤場景 ===")
    
    config = ConnectorConfig(
        name="error-test",
        type=ConnectorType.FILESYSTEM
    )
    
    connector = TestFileSystemConnector(config)
    
    # 1. 測試未初始化使用
    print("1. 測試未初始化使用...")
    
    # 嘗試在未初始化時讀取資源
    try:
        await connector.read_resource("file:///tmp/test.txt")
        print("   ❌ 應該拋出未初始化錯誤")
        return False
    except MCPConnectorError as e:
        print(f"   ✅ 正確捕獲未初始化錯誤: {e}")
    
    # 嘗試在未初始化時呼叫工具
    try:
        await connector.call_tool("read_file", {"path": "/tmp/test.txt"})
        print("   ❌ 應該拋出未初始化錯誤")
        return False
    except MCPConnectorError as e:
        print(f"   ✅ 正確捕獲未初始化錯誤: {e}")
    
    # 2. 測試資源不存在
    print("\n2. 測試資源不存在...")
    
    await connector.initialize()
    
    try:
        await connector.read_resource("file:///nonexistent/file.txt")
        print("   ❌ 應該拋出資源不存在錯誤")
        return False
    except MCPConnectorError as e:
        print(f"   ✅ 正確捕獲資源不存在錯誤: {e}")
    
    # 3. 測試工具不存在
    print("\n3. 測試工具不存在...")
    
    try:
        await connector.call_tool("nonexistent_tool", {})
        print("   ❌ 應該拋出工具不存在錯誤")
        return False
    except MCPConnectorError as e:
        print(f"   ✅ 正確捕獲工具不存在錯誤: {e}")
    
    await connector.cleanup()
    return True


async def main():
    """主測試函數"""
    print("🚀 開始 MCP 連接器系統手動測試")
    print("=" * 50)
    
    tests = [
        ("連接器配置", test_connector_config),
        ("連接器生命週期", test_connector_lifecycle),
        ("資源和工具功能", test_resources_and_tools),
        ("註冊表功能", test_registry),
        ("錯誤場景", test_error_scenarios),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 執行測試: {test_name}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                print(f"✅ {test_name} 測試通過")
            else:
                print(f"❌ {test_name} 測試失敗")
        except Exception as e:
            print(f"❌ {test_name} 測試異常: {e}")
    
    print("\n" + "=" * 50)
    print(f"🏁 測試完成: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有連接器測試通過！")
        return True
    else:
        print("⚠️  部分連接器測試失敗")
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