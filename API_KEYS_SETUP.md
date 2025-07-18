# 🔑 AI API 金鑰設定指南

## 📋 前置需求

由於您已有以下訂閱：
- ✅ ChatGPT Plus
- ✅ Claude Pro

您需要額外申請 API 金鑰，因為訂閱服務與 API 服務是分開計費的。

## ✅ 設定完成狀態

所有三個 AI 服務已成功設定並測試通過：
- 🎯 **OpenAI GPT-3.5 Turbo**: 正常運行
- 🎯 **Anthropic Claude 3.5 Sonnet**: 正常運行
- 🎯 **Google Gemini 1.5 Flash**: 正常運行

---

## 🔗 API 金鑰申請連結

### 1. OpenAI API 金鑰
**申請網址**: https://platform.openai.com/api-keys

**步驟**:
1. 使用您的 OpenAI 帳號登入
2. 點選右上角頭像 → "View API keys"
3. 點選 "Create new secret key"
4. 命名：`LocalMind-MCP-Development`
5. 複製金鑰 (格式：`sk-...`)

**重要**: 建議設定使用限制，避免意外高額費用。

### 2. Anthropic API 金鑰
**申請網址**: https://console.anthropic.com/

**步驟**:
1. 使用您的 Anthropic 帳號登入（或註冊新帳號）
2. 點選 "API Keys" → "Create Key"
3. 命名：`LocalMind-MCP-Development`
4. 複製金鑰 (格式：`sk-ant-...`)

### 3. Google AI Studio API 金鑰 (可選)
**申請網址**: https://aistudio.google.com/

**步驟**:
1. 使用 Google 帳號登入
2. 點選 "Get API key" → "Create API key"
3. 選擇 Google Cloud Project 或建立新的
4. 複製金鑰

**優點**: 提供免費額度，適合測試。

---

## ⚙️ 設定步驟

### 步驟 1: 編輯環境變數檔案

**⚠️ 安全提醒**: 環境變數檔案已加入 .gitignore，不會被提交到版控

1. **複製範本檔案**：
   ```bash
   cp .envs/.local/.django.example .envs/.local/.django
   ```

2. **編輯檔案**：`.envs/.local/.django`

```bash
# 將範本中的佔位符替換為實際金鑰

# 將 "your_openai_api_key_here" 替換為實際金鑰
OPENAI_API_KEY=sk-proj-你的實際OpenAI金鑰

# 將 "your_anthropic_api_key_here" 替換為實際金鑰
ANTHROPIC_API_KEY=sk-ant-你的實際Anthropic金鑰

# 將 "your_google_api_key_here" 替換為實際金鑰 (可選)
GOOGLE_API_KEY=你的實際Google金鑰
```

### 步驟 2: 重新啟動 Docker 容器

**⚠️ 重要**: 修改環境變數後，必須完全重新啟動容器才能載入新的環境變數。

```bash
# ✅ 方法 1: 使用 Makefile (推薦)
make reload-env

# ✅ 方法 2: 使用 justfile
just reload-env

# ✅ 方法 3: 標準 Docker Compose 指令
docker compose down && docker compose up -d

# ❌ 錯誤方法：只重啟服務 (環境變數不會更新)
# docker compose restart django  # 這樣無效！
# make up  # 如果容器已在運行，不會重新載入環境變數

# 確認服務運行
docker compose ps
```

**為什麼需要完全重新啟動？**
- Docker 容器的環境變數在容器**創建時**載入
- `restart` 只重啟容器內程序，**不會重新讀取** env_file
- 必須 `down` 然後 `up` 才能重新載入環境變數

### 步驟 3: 測試 API 金鑰

```bash
# ✅ 方法 1: 使用 Makefile (推薦)
make test-ai

# ✅ 方法 2: 使用 justfile
just test-ai

# ✅ 方法 3: 直接執行測試腳本
docker compose exec django python /app/scripts/setup_ai_keys.py
```

---

## 🧪 測試方法

### 方法 1: 使用測試腳本
```bash
# 使用專案自動化工具 (推薦)
make test-ai          # Makefile 方式
just test-ai          # justfile 方式

# 或直接執行
docker compose exec django python /app/scripts/setup_ai_keys.py
```

### 方法 2: 透過 API 測試
1. 訪問 http://localhost:8000/api/docs/
2. 使用 JWT Token 認證
3. 建立新對話：`POST /api/core/conversations/`
4. 發送訊息：`POST /api/core/conversations/{id}/messages/`
5. 確認收到 AI 回覆

### 方法 3: 直接服務測試
```bash
# 進入 Django shell
docker compose exec django python manage.py shell

# 執行測試代碼
from core.services.factory import AIServiceFactory
ai_service = AIServiceFactory.create_service()
response = ai_service.generate_response([{"role": "user", "content": "你好"}])
print(response.content)
```

---

## 💰 費用估算

### OpenAI GPT-3.5 Turbo (當前使用)
- **輸入**: ~$0.0005 / 1K tokens
- **輸出**: ~$0.0015 / 1K tokens
- **估算**: 100次對話約 $0.2-0.4 USD
- **實測**: 122 tokens ≈ $0.0002 USD

### Anthropic Claude 3.5 Sonnet (當前使用)
- **輸入**: ~$0.003 / 1K tokens
- **輸出**: ~$0.015 / 1K tokens
- **估算**: 100次對話約 $0.5-1 USD
- **實測**: 128 tokens ≈ $0.0007 USD

### Google Gemini 1.5 Flash (當前使用)
- **免費額度**: 每月 1500 requests/day
- **付費**: $0.00025 / 1K tokens (極便宜)
- **實測**: 39 tokens (免費額度內)

---

## 🛡️ 安全建議

1. **金鑰保護**
   - 絕對不要將 API 金鑰提交到 Git
   - 定期輪換金鑰
   - 設定使用限制

2. **監控使用量**
   - 定期檢查 API 使用量
   - 設定費用警告
   - 監控異常請求

3. **環境隔離**
   - 開發與生產環境使用不同金鑰
   - 限制 IP 存取（如可能）

---

## 🔧 故障排除

### 常見問題

**Q: 金鑰設定後仍然使用 Mock 服務？**
A: 檢查環境變數是否正確載入，使用 `docker compose down && docker compose up -d` 完全重新啟動容器。注意：`docker compose restart` 不會重新載入環境變數！

**Q: API 呼叫失敗？**
A:
1. 確認金鑰格式正確
2. 檢查帳戶餘額
3. 確認 API 限制設定

**Q: 回應速度慢？**
A: 真實 AI 服務回應時間 2-10 秒，比 Mock 服務慢是正常的。

### 除錯指令
```bash
# 檢查環境變數是否正確載入
docker compose exec django printenv | grep -E "(OPENAI|ANTHROPIC|GOOGLE).*KEY"

# 檢查 Django 設定
docker compose exec django python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()
from django.conf import settings
print('AI Services:', list(settings.AI_SERVICES_CONFIG.keys()))
"

# 檢查 AI 服務狀態
docker compose exec django python -c "
from core.services.factory import AIServiceFactory
service = AIServiceFactory.create_service()
print(f'Active service: {service.get_service_name()}')
print(f'Available: {service.is_available()}')
"

# 檢查服務日誌
docker compose logs django

# 檢查 Celery Worker 狀態
docker compose exec django celery -A config.celery_app inspect active
```

---

## 📞 支援

如遇到問題，請提供：
1. 錯誤訊息截圖
2. Docker 容器日誌
3. 使用的 API 金鑰服務（不要提供實際金鑰）

---

## 🎉 設定完成確認

### ✅ 成功測試結果

最新測試結果顯示所有 AI 服務正常運行：

```
🚀 AI 服務金鑰設定與測試
==================================================
🔍 檢查環境變數設定...

環境變數狀態:
  ✅ OPENAI_API_KEY: sk-proj-...
  ✅ ANTHROPIC_API_KEY: sk-ant-a...
  ✅ GOOGLE_API_KEY: AIzaSyAt...
  ✅ ENABLED_AI_SERVICES: openai,anthropic,google
  ✅ DEFAULT_AI_SERVICE: openai

🧪 測試個別 AI 服務...

🔸 測試 OpenAI 服務...
  ✅ OpenAI 回應: 成功 (122 tokens)

🔸 測試 Anthropic 服務...
  ✅ Anthropic 回應: 成功 (128 tokens)

🔸 測試 Google 服務...
  ✅ Google 回應: 成功 (39 tokens)

🏭 測試 AI 服務工廠和容錯機制...
  ✅ 工廠服務正常運作

⚙️ 測試 Celery 整合...
  ✅ Celery 整合測試通過

🎉 測試完成！
```

### 📊 系統狀態

- **✅ API 金鑰**: 全部設定完成
- **✅ AI 服務**: 3/3 正常運行
- **✅ 容錯機制**: 正常運作
- **✅ 異步處理**: Celery + Redis 正常
- **✅ 完整對話流程**: 已驗證

**下一步**: 系統已完全就緒，可進行生產環境部署或開始開發前端整合。
