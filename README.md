# LocalMind-MCP - 本地化 MCP 智慧助手平台

**LocalMind-MCP** 是一個基於 Model Context Protocol (MCP) 標準的本地化 AI 助手平台，專注於提供安全、可擴展的本地 AI 助手服務。

## 🎯 專案願景

本專案從成熟的 Gen AI 自動回覆平台基礎上演進，轉型為：
- **MCP 標準化整合平台**：支援多種資料源的標準化連接
- **本地化 AI 推理**：整合 Ollama 等本地 LLM 引擎
- **數位夥伴中心**：提供個人化的 AI 助手服務
- **企業級安全**：完整的認證與權限管理機制

## 🏗️ 技術架構

### 現有完成功能 (v1.0)
- ✅ **使用者管理系統**：基於 Django 的完整認證與角色管理
- ✅ **多 AI 服務整合**：支援 OpenAI、Anthropic、Google 等服務
- ✅ **異步任務處理**：Celery + Redis 架構
- ✅ **RESTful API**：完整的 API 文檔與測試
- ✅ **Docker 容器化**：生產就緒的部署方案

### 開發中功能 (v2.0 - MCP 轉換)
- 🔄 **MCP 協議支援**：標準化資料源連接協議
- 🔄 **Ollama 本地 LLM**：本地化 AI 推理引擎
- 🔄 **MCP 連接器生態**：檔案系統、GitHub、資料庫連接器
- 🔄 **混合架構**：Django Web + FastAPI MCP Server

This project implements a scalable backend system evolving from a Gen AI auto-reply platform to a comprehensive MCP-based local AI assistant platform, focusing on:

- MCP protocol-based data source integration
- Local LLM inference with Ollama
- User conversation and scene management
- Asynchronous AI reply processing via Celery and Redis
- Secure RESTful API endpoints for client integration
- Extendable architecture for MCP connector ecosystem

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

License: MIT

## Features

- 🔧 Built with cookiecutter-django
- ⚙️ Docker-ready with environment separation
- 📬 Supports Celery + Redis async workflow
- 📖 API documentation via drf-yasg (Swagger)
- 🧪 Pytest-based testing support

## Settings

Moved to [settings](https://cookiecutter-django.readthedocs.io/en/latest/1-getting-started/settings.html).

## Basic Commands

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

      $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Type checks

Running type checks with mypy:

    $ mypy genai_reply_backend

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

#### Running tests with pytest

    $ pytest

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/2-local-development/developing-locally.html#using-webpack-or-gulp).

### Celery

This app comes with Celery.

To run a celery worker:

```bash
cd genai_reply_backend
celery -A config.celery_app worker -l info
```

Please note: For Celery's import magic to work, it is important _where_ the celery commands are run. If you are in the same folder with _manage.py_, you should be right.

To run [periodic tasks](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html), you'll need to start the celery beat scheduler service. You can start it as a standalone process:

```bash
cd genai_reply_backend
celery -A config.celery_app beat
```

or you can embed the beat service inside a worker with the `-B` option (not recommended for production use):

```bash
cd genai_reply_backend
celery -A config.celery_app worker -B -l info
```

### Email Server

In development, it is often nice to be able to see emails that are being sent from your application. For that reason local SMTP server [Mailpit](https://github.com/axllent/mailpit) with a web interface is available as docker container.

Container mailpit will start automatically when you will run all docker containers.
Please check [cookiecutter-django Docker documentation](https://cookiecutter-django.readthedocs.io/en/latest/2-local-development/developing-locally-docker.html) for more details how to start all containers.

With Mailpit running, to view messages that are sent by your application, open your browser and go to `http://127.0.0.1:8025`

## Setup

To start the system with Docker:

```bash
docker compose up -d
```

## Deployment

The following details how to deploy this application.

### Docker

See detailed [cookiecutter-django Docker documentation](https://cookiecutter-django.readthedocs.io/en/latest/3-deployment/deployment-with-docker.html).

## Author
Maintained by Hughe Chen | AI Collaborative Development with Claude Code
