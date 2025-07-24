#!/usr/bin/env python3
"""
MCP 配置管理手動測試腳本

使用方法:
docker compose exec django python mcp/tests/manual_test_config.py
"""

import os
import sys
from mcp.config import MCPConfig, get_config, set_config
from mcp.exceptions import MCPConfigurationError


def test_default_config():
    """測試預設配置"""
    print("=== 測試預設配置 ===")
    
    config = MCPConfig()
    
    print(f"協議版本: {config.protocol_version}")
    print(f"最大連接數: {config.max_connections}")
    print(f"連接超時: {config.connection_timeout}s")
    print(f"Ollama 主機: {config.ollama_host}:{config.ollama_port}")
    print(f"預設模型: {config.default_model}")
    print(f"啟用連接器: {', '.join(config.enabled_connectors)}")
    print(f"快取啟用: {config.enable_cache}")
    print(f"日誌級別: {config.log_level}")
    
    # 測試配置驗證
    try:
        config.validate()
        print("✅ 預設配置驗證通過")
    except MCPConfigurationError as e:
        print(f"❌ 預設配置驗證失敗: {e}")
    
    return True


def test_env_config():
    """測試環境變數配置"""
    print("\n=== 測試環境變數配置 ===")
    
    # 設置測試環境變數
    test_env = {
        "MCP_PROTOCOL_VERSION": "2.0",
        "MCP_MAX_CONNECTIONS": "20",
        "MCP_OLLAMA_HOST": "test-ollama-host",
        "MCP_OLLAMA_PORT": "8080",
        "MCP_DEFAULT_MODEL": "llama3",
        "MCP_ENABLED_CONNECTORS": "filesystem,github,database",
        "MCP_LOG_LEVEL": "DEBUG",
        "MCP_ENABLE_CACHE": "false",
        "MCP_CACHE_TTL": "7200",
    }
    
    # 備份現有環境變數
    backup_env = {}
    for key in test_env:
        if key in os.environ:
            backup_env[key] = os.environ[key]
    
    try:
        # 設置測試環境變數
        for key, value in test_env.items():
            os.environ[key] = value
        
        # 從環境變數載入配置
        env_config = MCPConfig.from_env()
        
        print(f"協議版本: {env_config.protocol_version}")
        print(f"最大連接數: {env_config.max_connections}")
        print(f"Ollama 主機: {env_config.ollama_host}:{env_config.ollama_port}")
        print(f"預設模型: {env_config.default_model}")
        print(f"啟用連接器: {', '.join(env_config.enabled_connectors)}")
        print(f"快取啟用: {env_config.enable_cache}")
        print(f"日誌級別: {env_config.log_level}")
        print(f"快取 TTL: {env_config.cache_ttl}s")
        
        # 驗證環境變數是否正確載入
        assert env_config.protocol_version == "2.0"
        assert env_config.max_connections == 20
        assert env_config.ollama_host == "test-ollama-host"
        assert env_config.ollama_port == 8080
        assert env_config.default_model == "llama3"
        assert "github" in env_config.enabled_connectors
        assert env_config.log_level == "DEBUG"
        assert env_config.enable_cache is False
        assert env_config.cache_ttl == 7200
        
        # 測試配置驗證
        try:
            env_config.validate()
            print("✅ 環境變數配置驗證通過")
        except MCPConfigurationError as e:
            print(f"❌ 環境變數配置驗證失敗: {e}")
        
        return True
        
    finally:
        # 恢復環境變數
        for key in test_env:
            if key in backup_env:
                os.environ[key] = backup_env[key]
            else:
                os.environ.pop(key, None)


def test_invalid_config():
    """測試無效配置的處理"""
    print("\n=== 測試無效配置處理 ===")
    
    # 測試無效的最大連接數
    print("1. 測試無效的最大連接數...")
    try:
        invalid_config = MCPConfig(max_connections=0)
        invalid_config.validate()
        print("❌ 應該拋出配置錯誤")
        return False
    except MCPConfigurationError as e:
        print(f"✅ 正確捕獲錯誤: {e}")
    
    # 測試無效的端口號
    print("\n2. 測試無效的端口號...")
    try:
        invalid_config = MCPConfig(ollama_port=70000)
        invalid_config.validate()
        print("❌ 應該拋出配置錯誤")
        return False
    except MCPConfigurationError as e:
        print(f"✅ 正確捕獲錯誤: {e}")
    
    # 測試無效的日誌級別
    print("\n3. 測試無效的日誌級別...")
    try:
        invalid_config = MCPConfig(log_level="INVALID_LEVEL")
        invalid_config.validate()
        print("❌ 應該拋出配置錯誤")
        return False
    except MCPConfigurationError as e:
        print(f"✅ 正確捕獲錯誤: {e}")
    
    # 測試無效的連接器
    print("\n4. 測試無效的連接器...")
    try:
        invalid_config = MCPConfig(enabled_connectors=["filesystem", "invalid_connector"])
        invalid_config.validate()
        print("❌ 應該拋出配置錯誤")
        return False
    except MCPConfigurationError as e:
        print(f"✅ 正確捕獲錯誤: {e}")
    
    # 測試無效的環境變數值
    print("\n5. 測試無效的環境變數值...")
    
    # 備份環境變數
    backup_max_conn = os.environ.get("MCP_MAX_CONNECTIONS")
    
    try:
        os.environ["MCP_MAX_CONNECTIONS"] = "invalid_number"
        MCPConfig.from_env()
        print("❌ 應該拋出配置錯誤")
        return False
    except MCPConfigurationError as e:
        print(f"✅ 正確捕獲環境變數錯誤: {e}")
    finally:
        # 恢復環境變數
        if backup_max_conn:
            os.environ["MCP_MAX_CONNECTIONS"] = backup_max_conn
        else:
            os.environ.pop("MCP_MAX_CONNECTIONS", None)
    
    return True


def test_global_config():
    """測試全域配置管理"""
    print("\n=== 測試全域配置管理 ===")
    
    # 清除全域配置以確保測試獨立性
    import mcp.config
    mcp.config._global_config = None
    
    # 測試獲取預設全域配置
    print("1. 測試獲取預設全域配置...")
    config1 = get_config()
    config2 = get_config()
    
    if config1 is config2:
        print("✅ 全域配置單例模式正常")
    else:
        print("❌ 全域配置單例模式失敗")
        return False
    
    print(f"   全域配置協議版本: {config1.protocol_version}")
    
    # 測試設置自定義全域配置
    print("\n2. 測試設置自定義全域配置...")
    custom_config = MCPConfig(
        protocol_version="3.0",
        ollama_host="custom-host",
        max_connections=50
    )
    
    set_config(custom_config)
    retrieved_config = get_config()
    
    if retrieved_config.protocol_version == "3.0":
        print("✅ 自定義全域配置設置成功")
        print(f"   協議版本: {retrieved_config.protocol_version}")
        print(f"   Ollama 主機: {retrieved_config.ollama_host}")
        print(f"   最大連接數: {retrieved_config.max_connections}")
    else:
        print("❌ 自定義全域配置設置失敗")
        return False
    
    # 測試設置無效配置
    print("\n3. 測試設置無效全域配置...")
    try:
        invalid_config = MCPConfig(max_connections=-1)
        set_config(invalid_config)
        print("❌ 應該拋出配置錯誤")
        return False
    except MCPConfigurationError as e:
        print(f"✅ 正確阻止無效配置: {e}")
    
    return True


def test_config_to_dict():
    """測試配置轉換為字典"""
    print("\n=== 測試配置字典轉換 ===")
    
    config = MCPConfig(
        protocol_version="1.5",
        max_connections=15,
        ollama_host="dict-test-host",
        enabled_connectors=["filesystem", "database"]
    )
    
    config_dict = config.to_dict()
    
    print("配置字典內容:")
    for key, value in config_dict.items():
        print(f"  {key}: {value}")
    
    # 驗證字典內容
    expected_keys = [
        "protocol_version", "max_connections", "ollama_host", 
        "ollama_port", "enabled_connectors", "log_level"
    ]
    
    for key in expected_keys:
        if key not in config_dict:
            print(f"❌ 缺少配置項: {key}")
            return False
    
    if config_dict["protocol_version"] != "1.5":
        print("❌ 協議版本不匹配")
        return False
    
    if config_dict["max_connections"] != 15:
        print("❌ 最大連接數不匹配")
        return False
    
    print("✅ 配置字典轉換正確")
    return True


def main():
    """主測試函數"""
    print("🚀 開始 MCP 配置管理手動測試")
    print("=" * 50)
    
    tests = [
        ("預設配置", test_default_config),
        ("環境變數配置", test_env_config),
        ("無效配置處理", test_invalid_config),
        ("全域配置管理", test_global_config),
        ("配置字典轉換", test_config_to_dict),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 執行測試: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 測試通過")
            else:
                print(f"❌ {test_name} 測試失敗")
        except Exception as e:
            print(f"❌ {test_name} 測試異常: {e}")
    
    print("\n" + "=" * 50)
    print(f"🏁 測試完成: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有配置測試通過！")
        return True
    else:
        print("⚠️  部分配置測試失敗")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  測試被用戶中斷")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 測試執行失敗: {e}")
        sys.exit(1)