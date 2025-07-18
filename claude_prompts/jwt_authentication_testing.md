# 🧪 JWT 認證系統完整測試任務

你是 MaiAgent genai_reply_backend 專案的測試工程師，需要執行完整的 JWT 認證系統測試。

## 📋 專案背景
- Django 4.2.23 + DRF + simplejwt
- 自定義 User 模型 (email 登入)
- JWT 認證端點已實現
- Docker 本地開發環境

## 🎯 測試目標
驗證 JWT 認證系統的完整功能，包括註冊、登入、Token 使用、刷新、登出等流程。

## 🔧 測試環境設定
1. 確保 Docker 服務正常運行：`docker compose -f docker-compose.local.yml ps`
2. 檢查 Django 服務狀態：`docker compose -f docker-compose.local.yml logs django --tail=10`
3. 驗證基本服務可訪問：`curl -v http://localhost:8000/`

## 📝 測試案例執行清單

### 測試案例 1：用戶註冊驗證
**目標**：確認 Django Allauth 註冊功能正常
```bash
# 檢查註冊頁面
curl -X GET http://localhost:8000/accounts/signup/ -v
```
**預期結果**：返回 200 和註冊頁面 HTML

### 測試案例 2：測試用戶創建
**目標**：創建測試用戶用於後續認證測試
```bash
# 在 Django shell 中創建測試用戶
docker compose -f docker-compose.local.yml exec django python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
user, created = User.objects.get_or_create(
    email='test@example.com',
    defaults={'name': 'Test User', 'is_active': True}
);
if created:
    user.set_password('testpass123');
    user.save();
    print('✅ 測試用戶創建成功');
else:
    print('ℹ️ 測試用戶已存在');
print(f'用戶信息: {user.email}, 啟用狀態: {user.is_active}')
"
```

### 測試案例 3：JWT 登入功能
**目標**：測試 JWT 認證登入並獲取 Token
```bash
# JWT 登入請求
curl -X POST http://localhost:8000/api/users/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }' \
  -v
```
**預期回應格式**：
```json
{
  "success": true,
  "message": "登入成功",
  "data": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "Bearer",
    "user": {
      "id": 1,
      "email": "test@example.com",
      "display_name": "Test User",
      "role": "user",
      "is_verified": false
    }
  }
}
```

### 測試案例 4：JWT 保護端點訪問
**目標**：使用 Access Token 訪問受保護的 API 端點
```bash
# 替換 YOUR_ACCESS_TOKEN 為實際的 access token
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -v
```
**預期結果**：返回當前用戶的詳細信息

### 測試案例 5：Token 刷新功能
**目標**：使用 Refresh Token 獲取新的 Access Token
```bash
# 替換 YOUR_REFRESH_TOKEN 為實際的 refresh token
curl -X POST http://localhost:8000/api/users/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }' \
  -v
```
**預期回應**：
```json
{
  "success": true,
  "message": "Token 刷新成功",
  "data": {
    "access": "NEW_ACCESS_TOKEN",
    "token_type": "Bearer"
  }
}
```

### 測試案例 6：JWT 登出功能
**目標**：將 Refresh Token 加入黑名單
```bash
# 需要提供 access token 和 refresh token
curl -X POST http://localhost:8000/api/users/auth/logout/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }' \
  -v
```
**預期結果**：Token 成功加入黑名單

### 測試案例 7：黑名單 Token 驗證
**目標**：確認登出後的 Token 無法使用
```bash
# 使用已登出的 access token 訪問保護端點
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer BLACKLISTED_ACCESS_TOKEN" \
  -v
```
**預期結果**：返回 401 Unauthorized

### 測試案例 8：錯誤處理測試
**目標**：驗證各種錯誤情況的處理

#### 8.1 錯誤密碼
```bash
curl -X POST http://localhost:8000/api/users/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "wrongpassword"
  }'
```

#### 8.2 不存在的用戶
```bash
curl -X POST http://localhost:8000/api/users/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nonexistent@example.com",
    "password": "testpass123"
  }'
```

#### 8.3 無效 Token
```bash
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer invalid_token_here"
```

#### 8.4 缺少必要欄位
```bash
curl -X POST http://localhost:8000/api/users/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com"
  }'
```

## 🔍 驗證檢查項目

### Token 內容驗證
將獲得的 JWT Token 複製到 [jwt.io](https://jwt.io) 檢查 payload 是否包含：
- ✅ `user_id`: 用戶 ID
- ✅ `role`: 用戶角色
- ✅ `display_name`: 顯示名稱
- ✅ `is_verified`: 驗證狀態
- ✅ `exp`: 過期時間
- ✅ `iss`: 發行者 (maiagent-backend)

### Token 生命週期驗證
- ✅ Access Token 有效期：60 分鐘
- ✅ Refresh Token 有效期：7 天
- ✅ Token 自動輪轉機制
- ✅ 黑名單機制運作正常

## 📊 測試執行報告模板

```markdown
## JWT 認證測試執行報告

### 環境確認
- [ ] Docker 服務正常運行
- [ ] Django 服務可訪問
- [ ] 測試用戶創建成功

### 功能測試結果
- [ ] 用戶註冊頁面正常
- [ ] JWT 登入成功返回正確格式
- [ ] Access Token 可訪問保護端點
- [ ] Refresh Token 可獲取新 Access Token
- [ ] 登出功能正常運作
- [ ] 黑名單機制有效

### 錯誤處理測試
- [ ] 錯誤密碼正確處理
- [ ] 不存在用戶正確處理
- [ ] 無效 Token 正確處理
- [ ] 缺少欄位正確處理

### Token 驗證
- [ ] Token 包含所需 payload
- [ ] Token 生命週期正確
- [ ] 簽名驗證正常

### 發現問題
(記錄測試過程中發現的任何問題)

### 建議改進
(記錄可能的改進建議)
```

## 🚀 執行說明

1. **按順序執行**：請按照測試案例順序執行，每個案例都依賴前面的結果
2. **保存 Token**：執行測試案例 3 後，保存返回的 access 和 refresh token 用於後續測試
3. **替換變數**：將測試命令中的 `YOUR_ACCESS_TOKEN` 和 `YOUR_REFRESH_TOKEN` 替換為實際值
4. **記錄結果**：每個測試案例的執行結果都要記錄下來
5. **問題處理**：如果某個測試失敗，先檢查前置條件是否滿足，再進行問題排查

請按照此測試案例系統性地執行 JWT 認證功能驗證，並提供完整的測試執行報告。
