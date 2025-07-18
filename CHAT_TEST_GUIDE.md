# 🤖 LocalMind-MCP AI 對話測試指南

## 📋 快速開始

### 1. 啟動系統
```bash
# 啟動所有服務
make up

# 或使用 Docker Compose
docker compose up -d
```

### 2. 訪問測試頁面
- **首頁**: http://localhost:8000/
- **對話測試頁面**: http://localhost:8000/chat/test/
- **API 文檔**: http://localhost:8000/api/docs/

### 3. 創建測試用戶
```bash
# 創建超級用戶
make createsuperuser

# 或直接使用 Docker
docker compose exec django python manage.py createsuperuser
```

## 🔧 使用方法

### 步驟 1: 登入系統
1. 在對話測試頁面輸入您的 email 和密碼
2. 點擊「登入」按鈕
3. 系統會顯示登入成功訊息並開啟對話區塊

### 步驟 2: 檢查 AI 狀態 (可選)
1. 點擊「檢查 AI 狀態」按鈕
2. 查看各個 AI 服務的運行狀態：
   - ✅ OpenAI GPT-3.5 Turbo
   - ✅ Anthropic Claude 3.5 Sonnet
   - ✅ Google Gemini 1.5 Flash

### 步驟 3: 建立對話
1. 點擊「建立新對話」按鈕
2. 輸入對話標題（或使用默認標題）
3. 系統會自動載入對話列表

### 步驟 4: 發送訊息
1. 在訊息輸入框中輸入您想說的話
2. 點擊「發送訊息」按鈕或按 Enter 鍵
3. 您的訊息會立即顯示
4. 等待 2-10 秒，AI 會自動回覆

### 步驟 5: 對話管理
- **切換對話**: 點擊對話列表中的任一對話
- **查看歷史**: 選擇對話後會自動載入歷史訊息
- **刪除對話**: 點擊「刪除對話」按鈕

## 🚀 功能特色

### ✅ 已實現功能
- **JWT 認證**: 安全的使用者認證系統
- **多 AI 支援**: 三個不同的 AI 服務自動切換
- **即時對話**: 網頁界面即時顯示對話
- **對話管理**: 建立、選擇、刪除對話
- **歷史記錄**: 完整的對話歷史保存
- **異步處理**: 後台 Celery 處理 AI 回覆
- **容錯機制**: AI 服務故障時自動切換

### 🎯 測試重點
1. **認證流程**: 測試登入登出功能
2. **對話建立**: 測試新對話建立
3. **訊息發送**: 測試文字訊息傳送
4. **AI 回覆**: 確認 AI 正常回覆
5. **對話切換**: 測試多對話管理
6. **錯誤處理**: 測試各種錯誤情況

## 🔍 故障排除

### 常見問題

**Q: 登入失敗怎麼辦？**
A:
1. 確認 email 和密碼正確
2. 檢查是否已創建用戶帳號
3. 查看 Django 日誌：`make logs`

**Q: AI 沒有回覆？**
A:
1. 檢查 Celery Worker 是否運行：`docker compose ps`
2. 檢查 AI 服務狀態：`make test-ai`
3. 查看 Celery 日誌：`docker compose logs celeryworker`

**Q: 對話無法建立？**
A:
1. 確認已正確登入
2. 檢查網路連線
3. 查看瀏覽器控制台錯誤訊息

**Q: 頁面無法訪問？**
A:
1. 確認 Docker 服務已啟動：`docker compose ps`
2. 檢查端口 8000 是否被佔用
3. 重新啟動服務：`make reload-env`

### 除錯指令
```bash
# 查看所有服務狀態
docker compose ps

# 查看 Django 日誌
make logs

# 查看 Celery Worker 日誌
docker compose logs celeryworker

# 測試 AI 服務
make test-ai

# 重新啟動服務
make reload-env

# 進入 Django shell 除錯
make shell
```

## 📝 測試案例

### 基本對話測試
1. 登入系統
2. 建立新對話「測試對話」
3. 發送訊息：「你好，請介紹自己」
4. 確認收到 AI 回覆
5. 繼續對話：「你能做什麼？」

### 多對話測試
1. 建立對話 A：「技術討論」
2. 建立對話 B：「閒聊」
3. 在對話 A 中討論技術問題
4. 切換到對話 B 進行日常聊天
5. 驗證對話內容獨立保存

### 異常測試
1. 測試無效登入資料
2. 測試空白訊息發送
3. 測試網路中斷情況
4. 測試長訊息處理

## 🎭 演示腳本

適合向其他人展示系統的完整流程：

```
1. 開啟 http://localhost:8000/
   → 展示首頁和系統架構

2. 點擊「開始對話測試」
   → 進入測試界面

3. 輸入認證資訊並登入
   → 展示 JWT 認證

4. 點擊「檢查 AI 狀態」
   → 展示多 AI 服務狀態

5. 建立新對話「演示對話」
   → 展示對話管理

6. 發送訊息「請簡單介紹你的能力」
   → 展示即時對話功能

7. 切換到 API 文檔頁面
   → 展示完整 API 架構

8. 回到對話繼續互動
   → 展示完整用戶體驗
```

## 🔗 相關連結

- **API 文檔**: http://localhost:8000/api/docs/
- **管理後台**: http://localhost:8000/admin/
- **郵件測試**: http://localhost:8025/ (Mailpit)
- **Celery 監控**: http://localhost:5555/ (Flower)

---

**📞 技術支援**: 如有問題請查看系統日誌或聯繫開發團隊
