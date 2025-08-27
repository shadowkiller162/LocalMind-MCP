# LocalMind-MCP - 本地化 MCP 智慧助手平台

**LocalMind-MCP** 是一個基於 Model Context Protocol (MCP) 標準的本地化 AI 助手平台，專注於提供 **安全、可擴展** 的多代理 AI 服務。  
專案目標是從傳統的 GenAI 自動回覆平台演進，發展成 **企業級 AI 助手基礎架構**，能廣泛應用於 **電商 SaaS** 與 **LegalTech** 場景。

---

## 🎯 專案願景

- **MCP 標準化整合平台**：支援多種資料源的標準化連接  
- **本地化 AI 推理**：整合 Ollama 等本地 LLM 引擎  
- **數位夥伴中心**：提供個人化的 AI 助手服務  
- **企業級安全**：完整的認證與權限管理機制  

---

## 🏗️ 技術架構

### v1.0 已完成功能
- ✅ **使用者管理系統**：基於 Django 的完整認證與角色管理  
- ✅ **多 AI 服務整合**：支援 OpenAI、Anthropic、Google 等服務  
- ✅ **異步任務處理**：Celery + Redis 任務佇列  
- ✅ **RESTful API**：完整的 API 文檔與測試  
- ✅ **Docker 容器化**：生產就緒的部署方案  

### v2.0 開發中
- 🔄 **MCP 協議支援**：標準化資料源連接協議  
- 🔄 **Ollama 本地 LLM**：本地化 AI 推理引擎  
- 🔄 **MCP 連接器生態**：檔案系統、GitHub、資料庫連接器  
- 🔄 **混合架構**：Django Web + FastAPI MCP Server  

---

## 🌐 實務應用場景

### 電商 / Amazon SaaS
- 商品描述 → **RAG + Weaviate** → 自動生成廣告關鍵字與競品摘要  
- 可擴展至 **Amazon SP-API / Ads API**，支援廣告自動化與報表分析  

### LegalTech
- 契約文件 → Chunk + Embedding → 條款比對與風險提示  
- 可整合審閱標註模組，輔助律師與法務團隊進行高效率審閱  

---

## 🔧 核心技術實作
- **多模型支援**：OpenAI GPT、Anthropic Claude、Google Gemini（可熱插拔擴充）  
- **後端架構**：Django + DRF，JWT 認證，模組化設計  
- **非同步處理**：Redis + Celery 任務佇列，支援長任務與重試策略  
- **資料層**：PostgreSQL（請求/回應日誌、審計欄位、例外處理）  
- **檢索增強 (RAG)**：Weaviate 向量儲存與查詢，支援語意搜尋與文件摘要  
- **事件驅動**：Webhook + 任務佇列，可延伸至廣告報表匯入或法務審閱工作流  
- **容器化**：Docker Compose，環境隔離與健康檢查  

---

## 💡 架構亮點
- **智能路由**：依任務類型/成本/延遲門檻自動選擇模型，支援降級與備援策略  
- **API 抽象層**：統一多模型呼叫格式，降低上層耦合  
- **可觀測性**：請求追蹤 ID、任務狀態與耗時記錄，利於效能分析與故障排除  

---

## 🧪 API 範例
- `POST /api/v1/llm/complete`：多模型文字生成（指定 provider / model / max_tokens）  
- `POST /api/v1/rag/query`：上傳文件後的語意查詢（Weaviate 索引 + 摘要）  
- `POST /api/v1/agents/run`：觸發多步驟代理流程（可設定工具與約束）  

---

## 🚀 與職涯定位的關聯
此專案展現了 **「後端工程 + AI Agent 平台整合」** 的實作能力，對應到以下職缺需求：

- **TransBiz｜資深全端工程師（SaaS，全遠端）**  
  👉 FastAPI / asyncio、事件驅動架構、AI 多代理系統  

- **LegalTech 工程師（沛思坦 / 律果科技）**  
  👉 契約審閱、條款比對、RAG 與語意搜尋應用  

透過 LocalMind-MCP，可以清楚展現我從 **SRE → API 後端 → AI 平台工程師** 的轉型歷程。  

---

## 📚 文檔導航
- 🚀 [快速開始](docs/README.md)  
- 🔧 [環境設置指南](docs/human/setup/)  
- 🐳 [Docker 部署](docs/human/setup/docker_setup_complete_guide.md)  
- 🔑 [API 金鑰配置](docs/human/setup/API_KEYS_SETUP.md)  
- 👨‍💻 [開發文檔](docs/human/development/)  
- 🧪 [測試指南](docs/human/testing/)  
- 🤖 [AI Agent 框架](CLAUDE.md)  
- 📊 [專案進度](docs/ai_agent/milestone_tracking.md)  

---

## Features
- 🔧 Built with cookiecutter-django  
- ⚙️ Docker-ready with environment separation  
- 📬 Supports Celery + Redis async workflow  
- 📖 API documentation via drf-yasg (Swagger)  
- 🧪 Pytest-based testing support  

---

## Author
Maintained by **Hughe Chen** | AI Collaborative Development with Claude Code
