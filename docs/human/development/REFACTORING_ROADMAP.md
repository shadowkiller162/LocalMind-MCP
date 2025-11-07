# LocalMind-MCP 重構路線圖

> **基於 Linus Torvalds 方法論的代碼品質改進計劃**
>
> **生成日期：** 2025-11-07
> **參考標準：** [CLAUDE.md](../../../CLAUDE.md)
> **分析報告：** 基於 Linus 風格代碼審查

---

## 📊 當前技術債概況

### 🔴 嚴重超標文件 (5個)

| 排名 | 文件 | 行數 | 超標倍數 | 優先級 |
|------|------|------|----------|--------|
| 1 | `scripts/test_result_parser.py` | 661 | 2.2x | 🔴 HIGH |
| 2 | `mcp/tests/manual_test_connectors.py` | 613 | 2.0x | 🟡 MEDIUM |
| 3 | `genai_reply_backend/mcp_management/views.py` | 523 | 1.7x | 🔴 HIGH |
| 4 | `scripts/progress_updater.py` | 509 | 1.7x | 🟡 MEDIUM |
| 5 | `config/settings/base.py` | 445 | 1.5x | 🟢 LOW (Django配置) |

### 🟡 臨界狀態文件 (1個)

| 文件 | 行數 | 超標倍數 | 優先級 |
|------|------|----------|--------|
| `mcp/llm/unified_manager.py` | 332 | 1.1x | 🟡 MEDIUM (預防性) |

**總體評估：**
- 違規率：4.3%（5/117 文件）
- 技術債等級：🔴 HIGH
- 最大問題：`test_result_parser.py` 661行（全專案最大）

---

## 🎯 重構目標

### 可測量改進指標

**重構前：**
```
文件超標：5 個（4.3% 違規率）
最大文件：661 行（超標 220%）
最大函數：91 行（超標 82%）
技術債等級：🔴 HIGH
```

**重構後（預期）：**
```
文件超標：0 個（0% 違規率）
最大文件：~250 行（符合標準）
最大函數：~40 行（符合標準）
技術債等級：🟢 LOW
```

---

## 📅 重構路線圖

### Week 1: 重構 mcp_management/views.py（高優先級）

**Issue:** [refactor-views.md](../../../.github/ISSUE_TEMPLATE/refactor-views.md)

**目標：**
- 523 行 → ~380 行（7個文件）
- chat_send: 91行 → <50行
- 建立服務層架構

**關鍵任務：**
1. 創建 `services/` 目錄
2. 提取模型檢測服務
3. 提取 AI 響應處理服務
4. 拆分視圖文件

**可交付成果：**
- ✅ `services/model_detector.py`
- ✅ `services/ai_response_service.py`
- ✅ `views/dashboard_views.py`
- ✅ `views/chat_views.py`
- ✅ 所有測試通過

**回滾點：** `before-views-refactor`

---

### Week 2: 重構 test_result_parser.py（最大技術債）

**Issue:** [refactor-test-parser.md](../../../.github/ISSUE_TEMPLATE/refactor-test-parser.md)

**目標：**
- 661 行 → ~150 行（7個文件）
- 17 方法 → ~8 方法/類
- 按測試框架拆分

**關鍵任務：**
1. 創建 `parsers/` 目錄
2. 建立抽象基類 `BaseTestParser`
3. 拆分框架專用解析器
4. Facade 包裝保持向後相容

**可交付成果：**
- ✅ `parsers/base_parser.py`
- ✅ `parsers/pytest_parser.py`
- ✅ `parsers/django_parser.py`
- ✅ `parsers/coverage_parser.py`
- ✅ `ai_agent_automation.py` 正常運作

**回滾點：** `before-parser-refactor`

---

### Week 3: 優化 unified_manager.py（預防性重構）

**Issue:** [optimize-unified-manager.md](../../../.github/ISSUE_TEMPLATE/optimize-unified-manager.md)

**目標：**
- 332 行 → ~180 行（4個文件）
- 提取服務發現邏輯
- 提取模型緩存邏輯

**關鍵任務：**
1. 創建 `ServiceDiscovery` 類別
2. 創建 `ModelCache` 類別
3. 簡化 `UnifiedModelManager`
4. 依賴注入設計

**可交付成果：**
- ✅ `service_discovery.py`
- ✅ `model_cache.py`
- ✅ `health_checker.py`
- ✅ 簡化的 `unified_manager.py`

**回滾點：** `before-manager-optimize`

---

### Week 4: 建立自動化監控（基礎設施）

**Issue:** [setup-file-monitoring.md](../../../.github/ISSUE_TEMPLATE/setup-file-monitoring.md)

**目標：**
- Pre-commit hooks 設置
- GitHub Actions CI/CD
- 技術債報告自動生成

**關鍵任務：**
1. 安裝 pre-commit 框架
2. 創建文件大小檢查腳本
3. 創建函數長度檢查腳本
4. 設置 GitHub Actions workflow

**可交付成果：**
- ✅ `.pre-commit-config.yaml`
- ✅ `scripts/checks/check_file_size.py`
- ✅ `scripts/checks/check_function_length.py`
- ✅ `.github/workflows/code-quality.yml`
- ✅ 自動化技術債報告

**回滾點：** `before-monitoring-setup`

---

## 🔧 如何使用這些 Issue 模板

### 方法 1: 透過 GitHub Web UI

1. 訪問 [Issues 頁面](https://github.com/shadowkiller162/LocalMind-MCP/issues)
2. 點擊「New Issue」
3. 選擇對應的模板：
   - `Code Refactoring - mcp_management/views.py`
   - `Code Refactoring - test_result_parser.py`
   - `Code Optimization - unified_manager.py`
   - `Infrastructure - File Size Monitoring`
4. 填寫標題和內容（模板已預填）
5. 添加標籤和里程碑
6. 點擊「Submit new issue」

### 方法 2: 透過 GitHub CLI

```bash
# Week 1: Views 重構
gh issue create \
  --title "refactor: Split mcp_management/views.py into service layers" \
  --body-file .github/ISSUE_TEMPLATE/refactor-views.md \
  --label "refactoring,technical-debt,high-priority"

# Week 2: Parser 重構
gh issue create \
  --title "refactor: Split test_result_parser.py into framework-specific parsers" \
  --body-file .github/ISSUE_TEMPLATE/refactor-test-parser.md \
  --label "refactoring,technical-debt,high-priority,testing"

# Week 3: Manager 優化
gh issue create \
  --title "refactor: Extract service discovery and caching from unified_manager.py" \
  --body-file .github/ISSUE_TEMPLATE/optimize-unified-manager.md \
  --label "refactoring,technical-debt,medium-priority,prevention"

# Week 4: 監控設置
gh issue create \
  --title "chore: Setup file size monitoring and pre-commit hooks" \
  --body-file .github/ISSUE_TEMPLATE/setup-file-monitoring.md \
  --label "infrastructure,automation,code-quality"
```

### 方法 3: 手動複製內容

1. 打開對應的模板文件：
   - `.github/ISSUE_TEMPLATE/refactor-views.md`
   - `.github/ISSUE_TEMPLATE/refactor-test-parser.md`
   - `.github/ISSUE_TEMPLATE/optimize-unified-manager.md`
   - `.github/ISSUE_TEMPLATE/setup-file-monitoring.md`
2. 複製內容到新的 Issue
3. 調整需要的部分
4. 提交 Issue

---

## ✅ 每個 Issue 的驗收標準

### 共同標準（所有 Issue）

- [ ] mypy 檢查通過（0 錯誤）
- [ ] ruff 檢查通過（0 警告）
- [ ] pytest 全部通過
- [ ] 測試覆蓋率 ≥80%
- [ ] 現有功能零破壞
- [ ] 文檔已更新

### 特定標準

**Views 重構：**
- [ ] 所有文件 < 300 行
- [ ] 所有函數 < 50 行
- [ ] 服務層可獨立測試

**Parser 重構：**
- [ ] 所有文件 < 150 行
- [ ] 每個類別 < 10 方法
- [ ] `ai_agent_automation.py` 正常運作

**Manager 優化：**
- [ ] 主文件 < 200 行
- [ ] 組件可獨立測試
- [ ] 依賴注入設計正確

**監控設置：**
- [ ] Pre-commit hooks 運作
- [ ] CI/CD 自動檢查
- [ ] 技術債報告生成

---

## 📊 進度追蹤

### 里程碑設置

建議在 GitHub 建立以下里程碑：

1. **Milestone 1: Views Refactoring**
   - Due: Week 1 結束
   - Issues: #1 (refactor-views)

2. **Milestone 2: Parser Refactoring**
   - Due: Week 2 結束
   - Issues: #2 (refactor-test-parser)

3. **Milestone 3: Manager Optimization**
   - Due: Week 3 結束
   - Issues: #3 (optimize-unified-manager)

4. **Milestone 4: Monitoring Setup**
   - Due: Week 4 結束
   - Issues: #4 (setup-file-monitoring)

### 追蹤指標

每週更新以下指標：

```markdown
## Week X Progress

- [ ] 文件超標數：5 → X
- [ ] 最大文件行數：661 → X
- [ ] 最大函數行數：91 → X
- [ ] 技術債等級：🔴 → 🟡/🟢

**完成任務：**
- [x] Task 1
- [x] Task 2
- [ ] Task 3

**遇到問題：**
- Issue 1: ...
- Issue 2: ...

**下週計劃：**
- [ ] Task A
- [ ] Task B
```

---

## 🔄 回滾策略

每個 Issue 都有明確的回滾點：

| Issue | Git Tag | 回滾命令 |
|-------|---------|----------|
| Views | `before-views-refactor` | `git reset --hard before-views-refactor` |
| Parser | `before-parser-refactor` | `git reset --hard before-parser-refactor` |
| Manager | `before-manager-optimize` | `git reset --hard before-manager-optimize` |
| Monitoring | `before-monitoring-setup` | `git reset --hard before-monitoring-setup` |

**建議流程：**
1. 開始重構前打標籤
2. 完成後驗證所有測試通過
3. 如有問題，回滾到標籤點
4. 修復問題後再次嘗試

---

## 📚 相關文檔

### 核心指導文檔
- [CLAUDE.md](../../../CLAUDE.md) - Linus 方法論
- [README.md](../../../README.md) - 專案概述
- [OPTIMIZATION_TICKETS.md](OPTIMIZATION_TICKETS.md) - 優化需求清單

### Issue 模板
- [refactor-views.md](../../../.github/ISSUE_TEMPLATE/refactor-views.md)
- [refactor-test-parser.md](../../../.github/ISSUE_TEMPLATE/refactor-test-parser.md)
- [optimize-unified-manager.md](../../../.github/ISSUE_TEMPLATE/optimize-unified-manager.md)
- [setup-file-monitoring.md](../../../.github/ISSUE_TEMPLATE/setup-file-monitoring.md)

### 測試文檔
- [JWT 測試指南](../testing/jwt_authentication_complete_guide.md)
- [用戶登入測試](../testing/user_login_test.md)

---

## 💬 團隊協作建議

### Code Review 標準

每個 PR 必須檢查：

1. **代碼品質**
   - 文件行數 < 300
   - 函數長度 < 50
   - 複雜度 <= 10
   - 無特殊情況超過 2 個

2. **測試覆蓋**
   - 單元測試 ≥80%
   - 整合測試完整
   - 邊界情況覆蓋

3. **向後相容**
   - API 簽名不變
   - 現有測試通過
   - 功能零破壞

### 溝通渠道

- **GitHub Issues：** 任務追蹤和討論
- **GitHub PR：** 代碼審查
- **GitHub Projects：** 進度看板
- **週報：** 更新此文檔的進度追蹤部分

---

## 🎯 成功標準

**專案重構完成標準：**

- ✅ 所有 4 個 Issue 關閉
- ✅ 文件超標數：0
- ✅ 所有測試通過
- ✅ Pre-commit hooks 運作
- ✅ CI/CD 檢查通過
- ✅ 技術債等級：🟢 LOW
- ✅ 文檔更新完成

**長期維護標準：**

- ✅ 每週技術債報告
- ✅ 新代碼符合標準
- ✅ 持續改進文化

---

**"Talk is cheap. Show me the code."** - Linus Torvalds

_專注於解決實際問題，用最簡單的方法。_
