# Claude Code 共筆開發規則（簡化 Kent Beck 精神）

本文件為 Claude Code AI 共筆開發的行為指南，適用於中階工程師與 AI 工具的協作流程，融合 Kent Beck 的 TDD/Tidy First 原則並簡化為實務可執行的版本。

## 👤 角色與定位
- 你是與 Claude 合作的中階工程師，目標是維持程式結構清晰、模組邏輯明確。
- Claude 是你的共筆工程師，協助設計、補測試、調整結構，但最終決策與檢查仍由你負責。

## ✅ Claude 共筆工作原則
### 🧩 小步開發
- 每次任務只做一件事（新增功能 / 拆結構 / 加測試）

### 🧪 可測試設計優先
- 模組請設計為可抽離測試，優先測異常與邊界情況

### ✍️ Claude 提示語氣建議
- 明確描述：請建立 / 拆解 / 撰寫測試 / 重構
- 指定模組與檔案
- 請加中文註解與檔名標註

## 🗂 Claude 輸出與提交規範

| 類型         | 命名建議                    | Commit Message 範例              |
|--------------|-----------------------------|-----------------------------------|
| 結構性變更   | refactor_reply_task.md      | `refactor: 拆解 Celery 任務模組` |
| 行為性變更   | add_user_login_api.md       | `feat: 新增 JWT 登入 API`        |
| 測試補充     | test_conversation_api.md    | `test: 補上 conversation 測試`   |

## 🔁 Claude 協作提示語範例

```plaintext
1️⃣ 幫我建立 JWT 登入 view，請用 simplejwt 寫法
2️⃣ 幫我將 Celery 任務中的邏輯拆開
3️⃣ 幫我針對 chat.views 的 get_conversations 寫單元測試
```

## 🧪 測試建議
- 優先以 pytest + factory_boy 建立 CRUD 測試、異常處理、權限驗證

## 🎯 核心原則
1. 每次任務只專注一件事
2. 結構與行為變更分開處理
3. 測試先於重構，Claude 輸出需驗證
4. Commit 清楚標示目的與類型
