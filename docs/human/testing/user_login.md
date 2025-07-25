# 使用者登入模組（simplejwt）Claude Prompt 指令模版

你是我在 GenAI 回覆平台後端專案的共筆工程師，我們要建立登入驗證系統。

請幫我設計一套基於 `django-rest-framework-simplejwt` 的登入模組，包括：
1. login API view（接收帳號密碼、產生 access/refresh token）
2. serializer（進行帳號密碼驗證、錯誤處理）
3. 設定 simplejwt 的 lifetime、blacklist 等參數建議
4. 若使用者有 role 欄位，請在 payload 中加入對應權限

請直接提供對應程式碼與檔案位置建議，並以中英混寫方式加註解。
