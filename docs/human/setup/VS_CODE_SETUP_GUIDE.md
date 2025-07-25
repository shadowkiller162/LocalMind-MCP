# VS Code 開發環境設定指南

本指南說明如何在 VS Code 中設置 MaiAgent 專案的開發環境。

## 📋 前置需求

1. **VS Code** - 安裝最新版本的 Visual Studio Code
2. **Docker** - 確保 Docker 和 Docker Compose 已安裝並運行
3. **Python 3.11** - 本機 Python 環境（用於 IntelliSense 和除錯）

## 🔧 VS Code 設定文件

已為您創建完整的 VS Code 設定文件：

- **`.vscode/settings.json`** - 編輯器設定、Python 環境、代碼格式化
- **`.vscode/launch.json`** - 除錯配置（Django、測試、Celery）
- **`.vscode/tasks.json`** - 任務配置（Django、Docker、測試、代碼品質）
- **`.vscode/extensions.json`** - 推薦擴展套件
- **`.vscode/snippets.json`** - Django 代碼片段
- **`.vscode/keybindings.json`** - 自定義快捷鍵

## 🚀 快速開始

### 1. 安裝推薦擴展套件

打開 VS Code，按 `Ctrl+Shift+P` 開啟命令面板，輸入：
```
Extensions: Show Recommended Extensions
```

安裝所有推薦的擴展套件，包括：
- **Python** - Python 語言支援
- **Pylance** - Python 語言伺服器
- **Ruff** - Python 代碼格式化和檢查
- **Django** - Django 框架支援
- **Docker** - Docker 支援
- **GitLens** - Git 功能增強

### 2. 啟動開發環境

使用以下任一方式啟動服務：

#### 方式 A：使用任務（推薦）
按 `Ctrl+Shift+P` 開啟命令面板，選擇：
```
Tasks: Run Task > Docker: Start All Services
```

#### 方式 B：使用快捷鍵
按 `Ctrl+Shift+O U` 啟動所有 Docker 服務

#### 方式 C：使用終端機
```bash
make up
```

### 3. 驗證環境設定

服務啟動後，確認以下端點可正常訪問：

- **主要應用**：http://localhost:8000/
- **API 文檔**：http://localhost:8000/api/docs/
- **管理後台**：http://localhost:8000/admin/
- **AI 對話測試**：http://localhost:8000/chat/test/
- **Celery 監控**：http://localhost:5555/
- **郵件測試**：http://localhost:8025/

## 🎯 常用快捷鍵

### Django 開發
- `Ctrl+Shift+D R` - 啟動 Django 開發伺服器
- `Ctrl+Shift+D M` - 執行資料庫遷移
- `Ctrl+Shift+D K` - 建立新的遷移檔案
- `Ctrl+Shift+D S` - 開啟 Django Shell
- `Ctrl+Shift+D U` - 建立超級用戶

### 測試
- `Ctrl+Shift+T A` - 執行所有測試
- `Ctrl+Shift+T C` - 執行測試並產生覆蓋率報告
- `Ctrl+Shift+T D` - 在 Docker 中執行測試
- `Ctrl+Shift+F T` - 執行完整測試套件

### 代碼品質
- `Ctrl+Shift+Q C` - 執行 Ruff 代碼檢查
- `Ctrl+Shift+Q F` - 執行 Ruff 自動修復
- `Ctrl+Shift+Q R` - 執行 Ruff 格式化
- `Ctrl+Shift+Q M` - 執行 MyPy 類型檢查

### Docker 管理
- `Ctrl+Shift+O U` - 啟動所有 Docker 服務
- `Ctrl+Shift+O D` - 停止所有 Docker 服務
- `Ctrl+Shift+O L` - 查看 Docker 日誌
- `Ctrl+Shift+O S` - 進入 Django 容器 Shell

### AI 服務
- `Ctrl+Shift+A T` - 測試 AI 服務
- `Ctrl+Shift+A R` - 重新載入環境變數

## 🔍 除錯設定

### 1. Django 除錯
使用 `F5` 啟動除錯，預設配置：
- **Django Debug Server** - 本機除錯伺服器
- **Django Debug Server (Docker)** - Docker 容器除錯
- **Django Shell** - Django Shell 除錯
- **Django Tests** - 測試除錯

### 2. Celery 除錯
專門的 Celery 除錯配置：
- **Celery Worker** - Celery 工作者除錯
- **Celery Beat** - Celery 定時任務除錯

### 3. 自定義除錯
- **Django Management Command** - 自定義管理命令除錯
- **AI Service Test** - AI 服務測試除錯

## 🛠️ 任務配置

### Django 任務
- **Django: Start Development Server** - 啟動開發伺服器
- **Django: Run Migrations** - 執行資料庫遷移
- **Django: Make Migrations** - 建立遷移檔案
- **Django: Create Superuser** - 建立管理員用戶
- **Django: Shell** - 開啟 Django Shell

### 測試任務
- **Test: Run All Tests** - 執行所有測試
- **Test: Run with Coverage** - 執行測試並產生覆蓋率
- **Test: Coverage Report** - 產生覆蓋率報告

### 代碼品質任務
- **Code Quality: Run Ruff Check** - 代碼檢查
- **Code Quality: Run Ruff Fix** - 自動修復
- **Code Quality: Run Ruff Format** - 代碼格式化
- **Code Quality: Run MyPy** - 類型檢查

### Docker 任務
- **Docker: Start All Services** - 啟動所有服務
- **Docker: Stop All Services** - 停止所有服務
- **Docker: View Logs** - 查看服務日誌
- **Docker: Django Shell** - Django 容器 Shell

## 📝 代碼片段

提供豐富的 Django 代碼片段：

- `dj-model` - Django 模型模板
- `dj-viewset` - Django ViewSet 模板
- `dj-serializer` - Django 序列化器模板
- `dj-url` - Django URL 模板
- `dj-test` - Django 測試模板
- `dj-api-test` - Django API 測試模板
- `dj-celery-task` - Celery 任務模板
- `dj-form` - Django 表單模板

## 🔄 工作流程

### 日常開發流程
1. 啟動 Docker 服務：`Ctrl+Shift+O U`
2. 開始開發：編輯代碼，VS Code 自動格式化
3. 執行測試：`Ctrl+Shift+T A`
4. 代碼檢查：`Ctrl+Shift+Q C`
5. 提交代碼：使用 Git 功能

### 除錯流程
1. 設置中斷點
2. 按 `F5` 啟動除錯
3. 使用除錯控制台查看變數
4. 修改代碼並重新啟動

### 測試流程
1. 撰寫測試：使用 `dj-test` 或 `dj-api-test` 片段
2. 執行測試：`Ctrl+Shift+T A`
3. 查看覆蓋率：`Ctrl+Shift+T C`
4. 修復問題並重新測試

## 🐛 常見問題

### 1. Python 解釋器未找到
- 確保已安裝 Python 3.11
- 檢查 `settings.json` 中的 `python.defaultInterpreterPath`
- 手動選擇 Python 解釋器：`Ctrl+Shift+P` > `Python: Select Interpreter`

### 2. 擴展套件不工作
- 確認已安裝所有推薦擴展套件
- 重新載入 VS Code 視窗：`Ctrl+Shift+P` > `Developer: Reload Window`

### 3. Docker 服務無法啟動
- 確認 Docker 正在運行
- 檢查 Docker Compose 檔案：`docker-compose.yml`
- 查看 Docker 日誌：`Ctrl+Shift+O L`

### 4. 代碼格式化不工作
- 確認已安裝 Ruff 擴展套件
- 檢查 `settings.json` 中的格式化設定
- 手動格式化：`Shift+Alt+F`

## 📖 相關文檔

- **專案文檔**：`CLAUDE.md` - 專案開發指南
- **API 文檔**：`API_KEYS_SETUP.md` - AI 服務設定
- **測試指南**：`CHAT_TEST_GUIDE.md` - 對話測試指南
- **專案進度**：`claude_outputs/project_progress_report.md`

## 🎉 完成！

您的 VS Code 開發環境已設定完成！現在您可以：

1. 使用豐富的快捷鍵提高開發效率
2. 利用代碼片段快速建立 Django 組件
3. 使用內建除錯功能進行問題診斷
4. 執行完整的測試套件確保代碼品質

如有任何問題，請參考上方的常見問題解決方案或查看相關文檔。

祝您開發愉快！ 🚀
