# LM Studio 記憶體優化配置指南

## 目標
啟用 Auto-Evict 和 JIT Loading 來優化記憶體使用，避免同時載入多個大型模型。

## 當前狀態
❌ Auto-Evict: 未啟用 (多個模型同時在記憶體中)
❌ JIT Loading: 部分啟用 (載入時間 <2秒)
✅ TTL 支援: 已支援 (可設定模型過期時間)

## 配置步驟

### 1. LM Studio GUI 設定

#### 方法A: 透過 Developer 標籤頁
```
1. 打開 LM Studio 應用程式
2. 點擊左側導航的 "Developer" 或 "開發者" 標籤
3. 找到 "Server Settings" 或"伺服器設定" 區域
4. 查找 "Auto-Evict" 相關選項
5. 啟用 "Auto-Evict for JIT loaded models"
6. 設定預設 TTL (建議: 1800秒 = 30分鐘)
```

#### 方法B: 透過 Server 標籤頁
```
1. 在 LM Studio 中點擊 "Server" 標籤
2. 查看 "Advanced Settings" 或"進階設定"
3. 找到記憶體管理相關選項
4. 啟用 Auto-Evict
5. 配置 JIT Loading 設定
```

### 2. 建議的配置值

```yaml
Auto-Evict: ON (啟用)
Default TTL: 1800 seconds (30分鐘)
JIT Loading: ON (啟用) 
Max Models in Memory: 1 (Auto-Evict 模式)
```

### 3. 驗證配置

設定完成後，執行以下測試：

```bash
# 在專案目錄執行
make test-auto-evict
```

或手動測試：
```bash
docker compose exec django python manage.py shell -c "
from scripts.test_auto_evict import test_auto_evict_configuration
test_auto_evict_configuration()
"
```

### 4. 預期行為

**Auto-Evict 啟用後的行為：**
- 載入新模型會自動卸載舊模型
- 首次載入模型: 5-15秒 (JIT Loading)
- 切換模型: 5-15秒 (卸載舊模型 + 載入新模型)
- 記憶體使用: 大幅減少 (僅保留1個活躍模型)

**TTL 行為：**
- 模型閒置30分鐘後自動卸載
- 下次使用時重新 JIT 載入
- 有效節省長期記憶體使用

## 故障排除

### 問題1: Auto-Evict 設定找不到
```
解決方案:
1. 更新 LM Studio 到最新版本 (0.3.9+)
2. 檢查是否在 Beta 版本中
3. 重啟 LM Studio 應用程式
```

### 問題2: 設定不生效
```
解決方案:
1. 重啟 LM Studio Server
2. 清除已載入的模型
3. 檢查 LM Studio 日誌檔案
```

### 問題3: JIT Loading 太慢
```
優化方案:
1. 使用較小的模型進行測試
2. 確保 SSD 存儲空間充足
3. 檢查系統記憶體可用量
```

## 測試腳本

建立自動測試腳本來驗證配置：

```python
def test_auto_evict():
    # 1. 載入第一個模型 (應該是 JIT)
    # 2. 載入第二個模型 (應該卸載第一個)
    # 3. 檢查記憶體中只有一個模型
    # 4. 驗證載入時間 >5秒 (JIT 指標)
    pass
```

## 效能影響

**優點:**
- 記憶體使用降低 60-80%
- 支援更多模型切換
- 長期運行穩定性提升

**缺點:**
- 模型切換時間增加 (5-15秒)
- 首次載入延遲
- 需要更多 I/O 操作

## 推薦使用場景

- 系統記憶體有限 (<32GB)
- 需要在多個大型模型間切換
- 長期運行的服務環境
- 多用戶共享 LM Studio 資源

配置完成後，您的 LocalMind-MCP 系統將更有效地管理記憶體資源。