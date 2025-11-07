---
name: Code Refactoring - mcp_management/views.py
about: Refactor views.py following Linus methodology (523 lines → <300 lines)
title: 'refactor: Split mcp_management/views.py into service layers'
labels: 'refactoring, technical-debt, high-priority'
assignees: ''
---

## 📋 問題描述

**當前狀態：**
- 文件：`genai_reply_backend/mcp_management/views.py`
- 行數：523 / 300（超標 1.7 倍）🔴
- 函數數量：10 個視圖函數
- 最大函數：`chat_send` (91 行) - 接近超標（50行限制）

**違反規範：**
根據 [CLAUDE.md](../../CLAUDE.md) Linus 方法論：
- ❌ 文件行數 > 300 行
- ❌ 函數長度 > 50 行 (`chat_send` 91行)
- ❌ 職責混亂：模型檢測 + 聊天處理 + AI響應解析 + HTML清理

**核心問題：**
整個 MCP 管理界面的所有視圖都塞在一個文件中，導致：
- 測試困難（所有功能耦合在一起）
- 修改風險高（改一個地方可能影響其他功能）
- 代碼複用性差（服務邏輯與視圖邏輯混在一起）

## 🎯 重構目標

**可測量指標：**
- ✅ 所有文件 < 300 行
- ✅ 所有函數 < 50 行
- ✅ 職責單一（視圖只做路由，業務邏輯在 services）
- ✅ 測試覆蓋率維持 ≥80%

**預期結構：**
```
mcp_management/
├── views/
│   ├── __init__.py (30 行) - 統一導出
│   ├── dashboard_views.py (120 行) - 儀表板相關
│   ├── chat_views.py (150 行) - 聊天相關
│   └── connection_views.py (80 行) - 連接管理
├── services/
│   ├── __init__.py (20 行)
│   ├── model_detector.py (100 行) - LM Studio 模型檢測
│   └── ai_response_service.py (120 行) - AI 響應處理
└── utils/
    └── html_cleaner.py (50 行) - HTML 工具函數
```

## 🔧 實作步驟

### Phase 1: 建立服務層（不破壞現有功能）

**步驟 1.1: 創建服務目錄結構**
```bash
mkdir -p genai_reply_backend/mcp_management/services
mkdir -p genai_reply_backend/mcp_management/utils
touch genai_reply_backend/mcp_management/services/__init__.py
touch genai_reply_backend/mcp_management/utils/__init__.py
```

**步驟 1.2: 提取模型檢測服務**
創建 `services/model_detector.py`：
```python
class LMStudioModelDetector:
    """LM Studio 模型檢測服務"""

    def detect_models(self, config) -> dict:
        """檢測 LM Studio 中可用的模型

        Returns:
            dict: 包含模型列表和狀態信息
        """
        # 移動 detect_lmstudio_models 的邏輯到這裡
```

**步驟 1.3: 提取 AI 響應處理服務**
創建 `services/ai_response_service.py`：
```python
class AIResponseService:
    """AI 響應處理服務"""

    def parse_response(self, raw_content: str) -> dict:
        """解析 AI 原始響應"""
        # 移動 parse_ai_response 邏輯

    def process_message(self, message_content: str, user) -> dict:
        """處理 AI 訊息"""
        # 移動 process_ai_message 邏輯
```

**步驟 1.4: 提取 HTML 工具函數**
創建 `utils/html_cleaner.py`：
```python
def clean_html_whitespace(html_content: str) -> str:
    """清理 HTML 多餘空白"""
    # 移動 clean_html_whitespace 邏輯
```

### Phase 2: 重構視圖（保持 API 不變）

**步驟 2.1: 創建視圖目錄**
```bash
mkdir -p genai_reply_backend/mcp_management/views
```

**步驟 2.2: 拆分視圖文件**
按功能域分離：
- `dashboard_views.py` - mcp_dashboard, mcp_status
- `chat_views.py` - chat_send, chat_regenerate
- `connection_views.py` - mcp_reconnect

**步驟 2.3: 簡化 chat_send 函數**
```python
# 當前（91行）
def chat_send(request):
    # 驗證 + 配置 + 模型選擇 + AI調用 + 解析 + 渲染
    # 全塞在一起

# 改進（<50行）
def chat_send(request):
    # 1. 驗證輸入（早退出）
    if not request.POST.get('message'):
        return error_response("No message provided")

    # 2. 委托給服務層
    service = AIResponseService()
    result = service.process_message(
        message=request.POST['message'],
        user=request.user
    )

    # 3. 渲染響應
    return render_chat_message(result)
```

### Phase 3: 向後相容性保證

**步驟 3.1: 保持原有 API**
在 `views/__init__.py` 中：
```python
# 向後相容導出
from .dashboard_views import mcp_dashboard, mcp_status
from .chat_views import chat_send, chat_regenerate
from .connection_views import mcp_reconnect

# 保持工具函數可用
from ..utils.html_cleaner import clean_html_whitespace
from ..services.model_detector import LMStudioModelDetector

# Facade 包裝
def detect_lmstudio_models(config):
    """向後相容的包裝函數"""
    detector = LMStudioModelDetector()
    return detector.detect_models(config)

__all__ = [
    'mcp_dashboard', 'mcp_status', 'chat_send',
    'chat_regenerate', 'mcp_reconnect',
    'detect_lmstudio_models', 'clean_html_whitespace'
]
```

**步驟 3.2: 更新 URL 引用**
確認 `urls.py` 的引用路徑正確：
```python
# 保持不變或小幅調整
from .views import mcp_dashboard, chat_send  # 自動從 __init__.py 導入
```

## ✅ 驗收標準

### 代碼品質
- [ ] 所有文件 < 300 行
- [ ] 所有函數 < 50 行
- [ ] mypy 檢查通過（0 錯誤）
- [ ] ruff 檢查通過（0 警告）

### 功能測試
- [ ] 所有現有測試通過
- [ ] MCP 儀表板正常顯示
- [ ] 聊天功能正常運作
- [ ] AI 響應解析正確
- [ ] 模型檢測功能正常

### 架構檢查
- [ ] 視圖層只做路由，無業務邏輯
- [ ] 服務層可獨立測試
- [ ] 工具函數可複用
- [ ] 無循環依賴

### 向後相容性
- [ ] 現有 URL 路由不變
- [ ] 現有 API 簽名不變
- [ ] 現有功能零破壞
- [ ] 文檔已更新

## 🔄 回滾計劃

**Git 標籤：** `before-views-refactor`

**回滾命令：**
```bash
git tag before-views-refactor  # 重構前打標籤
git reset --hard before-views-refactor  # 如需回滾
```

**驗證腳本：**
```bash
# 檢查文件大小
wc -l genai_reply_backend/mcp_management/views.py

# 運行測試
docker compose exec django pytest genai_reply_backend/mcp_management/tests/ -v

# 檢查代碼品質
docker compose exec django ruff check genai_reply_backend/mcp_management/
docker compose exec django mypy genai_reply_backend/mcp_management/
```

## 📊 預期收益

**可測量改進：**
- 文件大小：523 行 → ~380 行（7個文件）✅
- 最大函數：91 行 → ~40 行 ✅
- 測試覆蓋率：維持 ≥80% ✅
- 技術債等級：🔴 HIGH → 🟡 MEDIUM

**長期價值：**
- ✅ 更容易添加新功能（職責清晰）
- ✅ 更容易測試（服務層可獨立測試）
- ✅ 更容易維護（修改影響範圍小）
- ✅ 更容易複用（服務可在其他地方使用）

## 📚 參考文檔

- [CLAUDE.md - Linus 方法論](../../CLAUDE.md)
- [優化票券範例](../../docs/human/development/OPTIMIZATION_TICKETS.md)
- [測試指南](../../docs/human/testing/jwt_authentication_complete_guide.md)
- [Docker 設置](../../docs/human/setup/docker_setup_complete_guide.md)

## 🏷️ 標籤

`refactoring` `technical-debt` `high-priority` `linus-methodology` `week-1`

## ⏱️ 預估工時

**3-4 天**

**分解：**
- Day 1: 創建服務層，提取業務邏輯
- Day 2: 拆分視圖文件，簡化函數
- Day 3: 測試 + 文檔更新
- Day 4: Code Review + 調整
