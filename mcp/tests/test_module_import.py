"""
MCP 模組導入測試

測試 MCP 模組的基本導入功能。
"""

import pytest


class TestModuleImport:
    """模組導入測試"""
    
    def test_import_mcp_module(self):
        """測試 MCP 模組基本導入"""
        import mcp
        
        assert hasattr(mcp, "__version__")
        assert hasattr(mcp, "__author__")
        assert mcp.__version__ == "0.1.0"
    
    def test_import_config(self):
        """測試配置模組導入"""
        from mcp import MCPConfig
        
        config = MCPConfig()
        assert config.protocol_version == "1.0"
    
    def test_import_exceptions(self):
        """測試例外類別導入"""
        from mcp import MCPError, MCPConnectionError, MCPProtocolError
        
        # 測試例外類別可以正常實例化
        base_error = MCPError("test error")
        assert str(base_error) == "test error"
        
        connection_error = MCPConnectionError("connection failed")
        assert "MCP_CONNECTION_ERROR" in str(connection_error)
        
        protocol_error = MCPProtocolError("protocol error")
        assert "MCP_PROTOCOL_ERROR" in str(protocol_error)
    
    def test_import_submodules(self):
        """測試子模組導入"""
        # 測試協議模組
        import mcp.protocol
        assert hasattr(mcp.protocol, "__name__")
        
        # 測試連接器模組
        import mcp.connectors
        assert hasattr(mcp.connectors, "__name__")
        
        # 測試 LLM 模組
        import mcp.llm
        assert hasattr(mcp.llm, "__name__")
    
    def test_all_exports(self):
        """測試 __all__ 導出"""
        import mcp
        
        expected_exports = [
            "MCPConfig",
            "MCPError", 
            "MCPConnectionError",
            "MCPProtocolError",
        ]
        
        for export in expected_exports:
            assert hasattr(mcp, export), f"Missing export: {export}"