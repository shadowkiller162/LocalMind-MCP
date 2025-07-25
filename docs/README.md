# LocalMind-MCP 文檔索引

本目錄包含 LocalMind-MCP 專案的完整文檔，按照 CLAUDE.md 指導原則組織。

## 📁 文檔結構

### 🤖 AI Agent 文檔 (`ai_agent/`)
AI Agent 自動化系統相關文檔，主要供程式自動更新使用：

- [`development_log.md`](ai_agent/development_log.md) - 開發歷程自動記錄
- [`milestone_tracking.md`](ai_agent/milestone_tracking.md) - 里程碑追蹤
- [`progress_report.md`](ai_agent/progress_report.md) - 進度報告

### 👥 人類可讀文檔 (`human/`)

#### 🔧 設置指南 (`human/setup/`)
系統安裝、配置和環境設置相關文檔：

- [`API_KEYS_SETUP.md`](human/setup/API_KEYS_SETUP.md) - API 金鑰配置指南
- [`VS_CODE_SETUP_GUIDE.md`](human/setup/VS_CODE_SETUP_GUIDE.md) - VS Code 開發環境設置
- [`CHAT_TEST_GUIDE.md`](human/setup/CHAT_TEST_GUIDE.md) - 聊天功能測試指南
- [`CLAUDE_CONVERSATION_MEMORY.md`](human/setup/CLAUDE_CONVERSATION_MEMORY.md) - Claude 對話記憶設置
- [`docker_setup_complete_guide.md`](human/setup/docker_setup_complete_guide.md) - Docker 容器化完整指南

#### 🏗️ 開發文檔 (`human/development/`)
專案開發、優化和進度相關文檔：

- [`OPTIMIZATION_TICKETS.md`](human/development/OPTIMIZATION_TICKETS.md) - 優化需求清單
- [`project_progress_report.md`](human/development/project_progress_report.md) - 專案進度報告
- [`development_retrospective_report.md`](human/development/development_retrospective_report.md) - 開發回顧報告

#### 🧪 測試文檔 (`human/testing/`)
測試案例、測試指南和測試報告：

- [`jwt_authentication_complete_guide.md`](human/testing/jwt_authentication_complete_guide.md) - JWT 認證完整測試指南
- [`JWT_測試案例.md`](human/testing/JWT_測試案例.md) - JWT 測試案例集
- [`jwt_authentication_testing.md`](human/testing/jwt_authentication_testing.md) - JWT 認證測試文檔
- [`user_login_test.md`](human/testing/user_login_test.md) - 使用者登入測試
- [`user_login.md`](human/testing/user_login.md) - 使用者登入功能說明

### 📦 歸檔文檔 (`archive/`)
已過時但保留參考的文檔：

- [`CLAUDE_OLD.md`](archive/CLAUDE_OLD.md) - 舊版 Claude 開發指南
- [`claude_guidelines.md`](archive/claude_guidelines.md) - 早期 Claude 協作規則

## 🔗 快速導航

### 新手入門
1. 閱讀 [../README.md](../README.md) - 專案概覽
2. 參考 [../CLAUDE.md](../CLAUDE.md) - AI Agent 開發框架
3. 按照 [`human/setup/`](human/setup/) 下的指南設置環境

### 開發者
1. 查看 [`human/development/`](human/development/) - 開發相關文檔
2. 參考 [`human/testing/`](human/testing/) - 測試指南
3. 追蹤 [`ai_agent/milestone_tracking.md`](ai_agent/milestone_tracking.md) - 開發進度

### 系統管理員
1. 設置指南：[`human/setup/docker_setup_complete_guide.md`](human/setup/docker_setup_complete_guide.md)
2. API 配置：[`human/setup/API_KEYS_SETUP.md`](human/setup/API_KEYS_SETUP.md)
3. 環境配置：[`human/setup/`](human/setup/) 目錄下所有文件

## 📋 文檔維護

本文檔結構遵循 [../CLAUDE.md](../CLAUDE.md) 中的 "📋 Update-Before-Create Documentation" 原則：
- ✅ 優先更新現有文檔
- ✅ 避免創建重複文檔
- ✅ 維持清晰的分類結構

如需添加新文檔，請先檢查是否可以更新現有文檔，並遵循現有的分類結構。