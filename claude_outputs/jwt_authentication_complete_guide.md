# JWT 認證系統完整指南

**整合日期：** 2025-01-15
**版本：** 完整實作 + 測試版
**適用專案：** MaiAgent genai_reply_backend

---

## 🎯 系統概述

本指南整合了 JWT 認證系統的完整實作，包含系統設計、程式碼實作、測試案例和實際測試報告。

## 📋 功能特色

### ✅ 核心功能
- **完整的 JWT 認證流程**：登入、刷新、登出
- **Role 權限整合**：JWT payload 包含使用者角色資訊
- **Token 安全機制**：黑名單、自動輪換、有效期控制
- **完整的錯誤處理**：中文錯誤訊息、統一 Response 格式
- **API 文檔整合**：Swagger/OpenAPI 文檔支援
- **權限控制系統**：基於 role 的多層級權限控制

### 🔒 安全性特色
- **Argon2 雜湊**：使用業界最安全的密碼雜湊算法
- **Token 黑名單機制**：登出時將 refresh token 加入黑名單
- **Token 自動輪換**：每次刷新都產生新的 refresh token
- **有效期控制**：Access Token 1小時、Refresh Token 7天
- **帳號狀態驗證**：檢查使用者是否為 active 狀態
- **Email 驗證整合**：可搭配 is_verified 欄位使用

## 🏗️ 系統架構

### 檔案結構
```
genai_reply_backend/users/api/
├── serializers_jwt.py      # JWT 序列化器
├── views.py               # API Views
├── urls.py                # URL 路由
└── permissions.py         # 權限控制

config/settings/base.py    # Django 設定
```

### 核心組件

#### 1. 自定義 JWT Token
```python
class CustomRefreshToken(RefreshToken):
    """自定義 RefreshToken，在 payload 中加入使用者 role 資訊"""

    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        # 加入使用者角色到 JWT payload
        token['role'] = user.role
        token['display_name'] = user.display_name or user.name
        token['is_verified'] = user.is_verified
        return token
```

#### 2. JWT 登入序列化器
```python
class JWTLoginSerializer(serializers.Serializer):
    """JWT 登入 Serializer - 處理帳號密碼驗證與 Token 生成"""

    email = serializers.EmailField(help_text="使用者 Email 帳號")
    password = serializers.CharField(write_only=True, help_text="使用者密碼")

    def validate(self, attrs):
        """驗證使用者帳號密碼"""
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError(
                "請提供完整的 email 與密碼",
                code="missing_credentials"
            )

        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=password
        )

        if not user:
            raise serializers.ValidationError(
                "無效的電子郵件或密碼，請檢查後重試",
                code="invalid_credentials"
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "此帳號已被停用，請聯繫管理員",
                code="inactive_user"
            )

        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        """生成 JWT Token 並回傳使用者資訊"""
        user = validated_data["user"]
        refresh = CustomRefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "token_type": "Bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "display_name": user.display_name or user.name,
                "role": user.role,
                "is_verified": user.is_verified,
            }
        }
```

#### 3. JWT 視圖
```python
class JWTLoginView(generics.GenericAPIView):
    """JWT 登入 API - 接收帳號密碼，返回 access/refresh token"""

    serializer_class = JWTLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """處理使用者登入請求"""
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        token_data = serializer.save()

        return Response({
            "success": True,
            "message": "登入成功",
            "data": token_data
        }, status=status.HTTP_200_OK)
```

#### 4. 權限控制系統
```python
class IsAdminUser(permissions.BasePermission):
    """僅允許 admin 角色使用者訪問"""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return (
            request.user.is_authenticated and
            request.user.role == User.Role.ADMIN
        )

class IsStaffOrAdmin(permissions.BasePermission):
    """允許 staff 或 admin 角色使用者訪問"""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return (
            request.user.is_authenticated and
            request.user.role in [User.Role.STAFF, User.Role.ADMIN]
        )
```

## ⚙️ 系統設定

### Django Simple JWT 設定
```python
# config/settings/base.py
SIMPLE_JWT = {
    # Token 有效期設定
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),  # Access token 1 小時有效
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),     # Refresh token 7 天有效

    # Token 自動刷新設定
    "ROTATE_REFRESH_TOKENS": True,                   # 刷新時產生新的 refresh token
    "BLACKLIST_AFTER_ROTATION": True,                # 舊 token 加入黑名單
    "UPDATE_LAST_LOGIN": True,                       # 更新使用者最後登入時間

    # 加密設定
    "ALGORITHM": "HS256",                            # 使用 HMAC SHA-256
    "SIGNING_KEY": env("DJANGO_SECRET_KEY"),
    "ISSUER": "maiagent-backend",                    # Token 發行者

    # Token 格式設定
    "AUTH_HEADER_TYPES": ("Bearer",),                # Authorization header 格式
    "USER_ID_FIELD": "id",                          # 使用者 ID 欄位
    "USER_ID_CLAIM": "user_id",                     # JWT payload 中的使用者 ID

    # 自定義序列化器
    "TOKEN_OBTAIN_SERIALIZER": "genai_reply_backend.users.api.serializers_jwt.JWTLoginSerializer",
    "TOKEN_REFRESH_SERIALIZER": "genai_reply_backend.users.api.serializers_jwt.TokenRefreshSerializer",
}
```

### URL 路由配置
```python
# genai_reply_backend/users/api/urls.py
urlpatterns = [
    # JWT 認證相關 endpoints
    path("auth/login/", JWTLoginView.as_view(), name="jwt-login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("auth/logout/", LogoutView.as_view(), name="jwt-logout"),
]
```

## 🧪 測試系統

### 測試覆蓋範圍
1. **登入功能測試**
   - ✅ 成功登入（正確 email + password）
   - ✅ 密碼錯誤處理
   - ✅ 無效 email 處理
   - ✅ 缺少必要欄位處理
   - ✅ 停用使用者登入處理

2. **Token Payload 測試**
   - ✅ 管理員使用者 payload 驗證
   - ✅ 職員使用者 payload 驗證
   - ✅ 未驗證使用者 payload 驗證
   - ✅ 自定義 claims 驗證（role, display_name, is_verified）

3. **Token 刷新測試**
   - ✅ 成功刷新 token
   - ✅ 無效 refresh token 處理
   - ✅ 缺少 refresh token 處理

4. **登出與黑名單測試**
   - ✅ 成功登出流程
   - ✅ Token 黑名單機制驗證
   - ✅ 黑名單資料庫記錄驗證

### 測試工廠
```python
class UserFactory(DjangoModelFactory[User]):
    email = Faker("email")
    name = Faker("name")
    display_name = Faker("name")
    role = fuzzy.FuzzyChoice(User.Role.choices, getter=lambda c: c[0])
    is_verified = True
    is_active = True

    @post_generation
    def password(self, create: bool, extracted: Sequence[Any], **kwargs):
        password = (
            extracted if extracted
            else Faker("password", length=42, special_chars=True, digits=True, upper_case=True, lower_case=True).evaluate(None, None, extra={"locale": None})
        )
        self.set_password(password)

    class Meta:
        model = User
        django_get_or_create = ["email"]
```

### 測試範例
```python
@pytest.mark.django_db
class TestJWTAuthentication:
    def test_successful_login(self, api_client: APIClient, authenticated_user: User):
        """測試成功登入流程"""
        url = reverse("users_api:jwt-login")
        data = {
            "email": authenticated_user.email,
            "password": authenticated_user.plain_password,
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["message"] == "登入成功"

        # 驗證回傳的 token 結構
        data = response_data["data"]
        assert "access" in data
        assert "refresh" in data
        assert data["token_type"] == "Bearer"
```

## 🔐 實際測試報告

### 測試環境
- **測試日期**: 2025-07-15
- **Django 版本**: 4.2.23
- **測試框架**: 手動 cURL 測試
- **Docker 環境**: 本地開發環境

### 測試結果統計
- **測試案例總數**: 7 個
- **成功案例**: 7 個 (100%)
- **失敗案例**: 0 個 (0%)
- **整體評估**: ✅ 全部通過

### 功能覆蓋率
- ✅ **用戶認證**: 100% 覆蓋
- ✅ **Token 管理**: 100% 覆蓋
- ✅ **API 保護**: 100% 覆蓋
- ✅ **錯誤處理**: 100% 覆蓋
- ✅ **安全機制**: 100% 覆蓋

### JWT Token Payload 範例
```json
{
  "user_id": 2,
  "role": "user",
  "display_name": "Test User",
  "is_verified": false,
  "token_type": "access",
  "exp": 1683456789,
  "iat": 1683453189,
  "jti": "abc123",
  "iss": "maiagent-backend"
}
```

## 🌐 API 使用範例

### 1. 使用者登入
```bash
curl -X POST http://localhost:8000/api/users/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
```

**回應範例：**
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
      "email": "user@example.com",
      "display_name": "用戶名稱",
      "role": "user",
      "is_verified": true
    }
  }
}
```

### 2. 使用 Access Token 訪問受保護資源
```bash
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer <access_token>"
```

### 3. 刷新 Token
```bash
curl -X POST http://localhost:8000/api/users/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

### 4. 使用者登出
```bash
curl -X POST http://localhost:8000/api/users/auth/logout/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

## 🛡️ 安全性評估

### 密碼安全
- ✅ **Argon2 雜湊**: 使用業界最安全的密碼雜湊算法
- ✅ **Salt 機制**: 每個密碼都有唯一的 salt
- ✅ **雜湊強度**: 使用 Argon2id 變體，抗時間和記憶體攻擊

### Token 安全
- ✅ **HMAC SHA-256**: 使用安全的簽名算法
- ✅ **適當的過期時間**: Access Token 1小時，Refresh Token 7天
- ✅ **Token 輪轉**: 刷新時產生新的 refresh token
- ✅ **黑名單機制**: 登出後 token 無法重複使用
- ✅ **JTI 唯一性**: 每個 token 都有唯一的 jti 識別碼

### API 安全
- ✅ **Bearer Token 認證**: 標準的 Authorization header 格式
- ✅ **端點保護**: 受保護的 API 正確驗證 token
- ✅ **錯誤處理**: 適當的錯誤訊息，不洩露敏感資訊

## 🎯 系統優勢

- 🔐 **高安全性**: Argon2 + JWT + Token 黑名單
- 🚀 **高性能**: 無狀態認證，適合分散式部署
- 📱 **適用性廣**: 支援 Web、Mobile、API 等多種客戶端
- 🛠️ **易於維護**: 清晰的代碼結構和完整的文檔
- 🧪 **完整測試**: 涵蓋所有功能的測試套件

## 📈 改進建議

### 短期改進
1. **用戶資訊完整性**: UserSerializer 可以包含更多用戶資訊
2. **速率限制**: 可以添加登入嘗試次數限制
3. **審計日誌**: 可以記錄認證相關的操作日誌

### 長期改進
1. **多因素認證**: 未來可以考慮支援 MFA
2. **SSO 整合**: 支援第三方登入（Google、GitHub 等）
3. **權限細粒度控制**: 更詳細的權限管理系統

## 🚀 部署建議

### 環境配置
1. **環境變數**: 確保生產環境使用安全的 SECRET_KEY
2. **HTTPS**: 生產環境必須使用 HTTPS 傳輸
3. **Redis**: 確保 Redis 連接穩定，用於 Token 黑名單

### 監控與維護
1. **監控**: 建議監控認證失敗次數和異常行為
2. **備份**: 定期備份用戶資料和 Token 黑名單
3. **日誌**: 記錄重要的認證事件

## 🔄 前端整合

### Axios 攔截器範例
```javascript
// 自動刷新 token 的 axios 攔截器範例
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // 嘗試刷新 token
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post('/api/users/auth/refresh/', {
            refresh: refreshToken
          });
          localStorage.setItem('access_token', response.data.data.access);
          // 重新發送原始請求
          return axios(error.config);
        } catch (refreshError) {
          // 刷新失敗，導向登入頁面
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);
```

## 📝 總結

JWT 認證系統已完整實現所有要求的功能：
- ✅ Login API view 與 serializer
- ✅ SimpleJWT 完整設定
- ✅ Role 權限整合到 JWT payload
- ✅ Token 安全機制（blacklist、rotation）
- ✅ 完整的錯誤處理與 API 文檔
- ✅ 基於 role 的權限控制系統
- ✅ 完整的測試套件
- ✅ 實際測試驗證

系統採用現代安全最佳實踐，提供穩定可靠的認證服務，為 MaiAgent 平台的用戶管理奠定了堅實基礎。

---

**整合來源檔案:**
- `user_login.md` - JWT 登入模組實作
- `user_login_test.md` - JWT 測試案例實作
- `jwt_authentication_test_report.md` - 實際測試執行報告

**最後更新:** 2025-01-15
