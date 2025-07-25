# 🧪 測試任務：JWT 登入模組測試

請協助撰寫 JWT 登入相關功能的 pytest 測試，請使用 pytest-django 框架與 factory_boy 工具。

## 📂 測試檔案位置：
`tests/users/test_auth.py`

## ✅ 測試項目需求：

1. 成功登入：
   - 給定正確 email 與 password，應回傳 access + refresh token
2. 密碼錯誤：
   - 回傳 401，並顯示錯誤訊息
3. 欄位缺失：
   - 當缺少 email 或 password 時，應回傳 400
4. Token Payload 驗證：
   - 登入成功後，解碼 access token，確認 payload 包含：
     - role
     - display_name
     - is_verified
5. 登出與 blacklist：
   - 登入後，使用 refresh token 登出
   - 驗證 token 進入 blacklist（使用 token_blacklist app 查詢）

## 🧱 建議測試結構：
- 使用 `pytest.mark.django_db` 標註測試
- 使用 `client.post()` 進行 API 測試
- 使用 factory 建立 `UserFactory`
- 使用 `RefreshToken(token).check_blacklist()` 驗證登出行為

## 📌 注意事項：
- 請勿混合多個測試在單一函數中，請保持每個測試案例單一責任
- 若你需要額外建構 fixtures 或 helper utils，可一併提供
