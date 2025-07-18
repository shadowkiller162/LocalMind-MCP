# JWT 認證系統測試案例

## 測試環境
- 伺服器：http://localhost:8000
- 測試框架：手動 cURL 測試
- 資料庫：PostgreSQL (Docker)

## 測試準備
1. 確保 Docker 服務正常運行
2. 創建測試用戶：test@example.com / testpass123

## 測試案例

### 案例1：用戶註冊驗證
**目標**：驗證 Django Allauth 註冊功能
**端點**：`GET /accounts/signup/`
**方法**：GET
**預期結果**：返回註冊頁面 HTML

### 案例2：JWT 登入功能
**目標**：測試 JWT 認證登入
**端點**：`POST /api/users/auth/login/`
**請求資料**：
```json
{
  "email": "test@example.com",
  "password": "testpass123"
}
```
**預期回應**：
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

### 案例3：JWT 保護端點訪問
**目標**：驗證 JWT Token 認證機制
**端點**：`GET /api/users/me/`
**認證**：Bearer Token
**預期結果**：返回當前用戶資訊

### 案例4：JWT Token 刷新
**目標**：測試 Refresh Token 機制
**端點**：`POST /api/users/auth/refresh/`
**請求資料**：
```json
{
  "refresh": "YOUR_REFRESH_TOKEN"
}
```
**預期回應**：新的 Access Token

### 案例5：JWT 登出
**目標**：測試 Token Blacklist 機制
**端點**：`POST /api/users/auth/logout/`
**請求資料**：
```json
{
  "refresh": "YOUR_REFRESH_TOKEN"
}
```
**預期結果**：Token 被列入黑名單

### 案例6：無效認證測試
**目標**：驗證錯誤處理
**測試項目**：
- 錯誤密碼
- 不存在用戶
- 無效 Token
- 過期 Token

## 測試執行命令

### 登入測試
```bash
curl -X POST http://localhost:8000/api/users/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

### 保護端點測試
```bash
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Token 刷新測試
```bash
curl -X POST http://localhost:8000/api/users/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"YOUR_REFRESH_TOKEN"}'
```

### 登出測試
```bash
curl -X POST http://localhost:8000/api/users/auth/logout/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"refresh":"YOUR_REFRESH_TOKEN"}'
```

## 驗證要點
1. JWT Token 格式正確
2. 包含用戶角色資訊
3. Token 生命週期符合設定
4. 黑名單機制正常運作
5. 錯誤處理適當

## 測試檢查清單
- [ ] 註冊頁面可訪問
- [ ] JWT 登入成功返回 Token
- [ ] Access Token 可訪問保護端點
- [ ] Refresh Token 可獲取新 Access Token
- [ ] 登出後 Token 被列入黑名單
- [ ] 錯誤情況正確處理
