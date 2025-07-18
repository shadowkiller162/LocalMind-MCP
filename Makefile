# 啟動與關閉
up:
	docker compose up -d

down:
	docker compose down

# 開啟 Shell
shell:
	docker compose exec django bash

# Django 指令通用入口
manage:
	docker compose exec django python manage.py $(cmd)

# 常用快捷指令
migrate:
	docker compose exec django python manage.py migrate

makemigrations:
	docker compose exec django python manage.py makemigrations

createsuperuser:
	docker compose exec django python manage.py createsuperuser

# 測試與 Lint
test:
	docker compose exec django pytest

lint:
	docker compose exec django ruff check .

# 查看日誌
logs:
	docker compose logs -f django

# 重新載入環境變數 (停止並重新啟動所有服務)
reload-env:
	@echo "🔄 重新載入環境變數..."
	docker compose down
	docker compose up -d
	@echo "✅ 環境變數重新載入完成"
	@echo "💡 使用 'make test-ai' 測試 AI 服務"

# 測試 AI 服務配置
test-ai:
	docker compose exec django python /app/scripts/setup_ai_keys.py
