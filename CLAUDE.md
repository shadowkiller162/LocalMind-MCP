# CLAUDE.md - AI Agent Development Framework

> **Purpose**: Universal development rules and guidelines for Claude Code CLI  
> **Scope**: Django & FastAPI projects  
> **Version**: v2.0  
> **Last Updated**: 2025-07-24

---

## 🤖 MANDATORY AI AGENT EXECUTION RULES

### 1. **🐳 Docker Environment Enforcement**
```bash
# ✅ REQUIRED - All commands must execute in Docker
docker compose exec django python manage.py migrate
docker compose exec django pytest
docker compose exec app uvicorn main:app --reload

# ❌ FORBIDDEN - Never execute on host
python manage.py migrate
pytest
uvicorn main:app --reload
```

### 2. **🌐 English-Only Git Standards**
```bash
# ✅ REQUIRED - Professional English commits
git commit -m "Implement user authentication system"
git commit -m "Add comprehensive API testing suite"

# ❌ FORBIDDEN - Non-English commits
git commit -m "實作用戶認證系統"
```

### 3. **📋 Update-Before-Create Documentation**
```bash
# ✅ REQUIRED - Check existing files first
find . -name "*.md" | grep -i [keyword]
# Then update existing documentation

# ❌ FORBIDDEN - Create without checking
touch NEW_FILE.md
```

---

## 📊 AUTOMATED PROGRESS TRACKING SYSTEM

### **AI Agent Auto-Update Triggers**
- ✅ **Function Implementation Complete**: Update `docs/ai_agent/development_log.md`
- ✅ **Tests Pass**: Update `docs/ai_agent/test_results.md`
- ✅ **Milestone Achieved**: Update `docs/ai_agent/milestone_tracking.md`
- ✅ **Integration Success**: Update `docs/ai_agent/progress_report.md`

### **Update Template Format**
```markdown
## [TIMESTAMP] Feature Implementation: [FEATURE_NAME]

### ✅ Completed Tasks
- [x] Core business logic
- [x] API endpoints (Django views / FastAPI routes)
- [x] Data models
- [x] Unit tests (>90% coverage)
- [x] Integration tests
- [x] Frontend integration tests (if applicable)

### 📊 Test Results
- Unit Tests: [PASS_COUNT]/[TOTAL_COUNT] passed
- Integration Tests: [PASS_COUNT]/[TOTAL_COUNT] passed
- Coverage: [PERCENTAGE]%

### 🔄 Next Steps
- [ ] [Next milestone task]
```

---

## 🏗️ UNIVERSAL PROJECT ARCHITECTURE

### **Framework-Agnostic Structure**
```
project_root/
├── README.md                    # Human-readable project overview
├── CLAUDE.md                    # AI Agent development guide
├── docs/
│   ├── ai_agent/                # AI Agent documentation
│   │   ├── development_log.md   # Auto-updated development history
│   │   ├── progress_report.md   # Auto-updated progress tracking
│   │   ├── milestone_tracking.md # Feature-based milestone tracking
│   │   └── test_results.md      # Auto-updated test results
│   └── human/                   # Human-readable documentation
├── tests/                       # Test suites
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── [framework_specific_structure]
```

### **Django-Specific Structure**
```
django_project/
├── apps/
│   ├── users/          # User management
│   ├── core/           # Business logic
│   └── api/            # API endpoints
├── config/
│   ├── settings/
│   └── urls.py
├── requirements/
│   ├── base.txt
│   ├── local.txt
│   └── production.txt
└── docker-compose.yml
```

### **FastAPI-Specific Structure**
```
fastapi_project/
├── app/
│   ├── api/            # API routes
│   ├── core/           # Business logic
│   ├── models/         # Data models
│   └── services/       # Service layer
├── tests/
├── pyproject.toml      # Poetry/pip-tools configuration
└── docker-compose.yml
```

---

## 🧪 FUNCTION-BASED TDD MILESTONE FRAMEWORK

### **Milestone Template**
```markdown
## Milestone: [FUNCTION_NAME]

### 📋 Function Scope
**Business Requirements**:
- [Primary business objective]
- [User story or use case]
- [Success criteria]

**Technical Requirements**:
- [API endpoints to implement]
- [Data models needed]
- [External integrations]

### 🧪 Testing Requirements (MANDATORY)

#### Unit Tests (>90% Coverage)
- [ ] Core business logic functions
- [ ] Model validations and methods
- [ ] Utility functions and helpers

#### Integration Tests
- [ ] Database operations (Django ORM / SQLAlchemy)
- [ ] External API calls (mocked and real)
- [ ] Authentication and authorization

#### Framework-Specific Tests
**Django Projects**:
- [ ] View/ViewSet functionality
- [ ] URL routing
- [ ] Template rendering (if applicable)
- [ ] Admin interface (if applicable)

**FastAPI Projects**:
- [ ] Route handlers
- [ ] Dependency injection
- [ ] Request/Response validation
- [ ] OpenAPI documentation generation

#### Frontend Integration Tests (If Applicable)
- [ ] API response format validation
- [ ] Error handling and status codes
- [ ] Authentication flow
- [ ] Real browser/client testing

### ✅ Completion Criteria
- [ ] All tests pass (unit + integration + e2e)
- [ ] Code quality checks pass (ruff, mypy, etc.)
- [ ] API documentation updated
- [ ] Progress documentation auto-updated
- [ ] Git commit with English message
- [ ] Milestone tagged in Git

### 🔄 Rollback Configuration
- **Git Tag**: `milestone-[function-name]`
- **Rollback Command**: `git reset --hard milestone-[function-name]`
- **Verification Script**: `./scripts/verify_[function-name].sh`
```

---

## 🔧 FRAMEWORK-SPECIFIC CONFIGURATIONS

### **Django Configuration Standards**
```python
# settings/base.py
import environ
env = environ.Env()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST', default='localhost'),
        'PORT': env('POSTGRES_PORT', default='5432'),
    }
}

# Testing configuration
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
```

### **FastAPI Configuration Standards**
```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()

# app/main.py
from fastapi import FastAPI
from app.api import router

app = FastAPI(
    title="Project API",
    description="API documentation",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")
```

---

## 📋 DEVELOPMENT WORKFLOW (MANDATORY)

### **Pre-Development Checklist**
- [ ] Confirm execution in correct Docker container
- [ ] Check existing file structure to avoid duplication
- [ ] Prepare English commit message format
- [ ] Verify network configuration for containers
- [ ] Set appropriate timeout settings for external services

### **Development Cycle**
```
1. Update milestone in docs/ai_agent/milestone_tracking.md
2. Write failing tests (TDD approach)
3. Implement minimal viable solution
4. Pass all tests (unit + integration + e2e)
5. Update progress documentation (AUTO)
6. Commit with English message
7. Tag milestone in Git
8. Prepare next milestone
```

### **Post-Development Verification**
- [ ] All tests pass in Docker environment
- [ ] Git commit uses standard English format
- [ ] Documentation updated (not created anew)
- [ ] Configuration supports different environments
- [ ] Code quality meets project standards

---

## 🔍 QUALITY ASSURANCE STANDARDS

### **Code Quality Tools**
```toml
# pyproject.toml (Both Django & FastAPI)
[tool.ruff]
line-length = 120
target-version = "py311"
extend-select = ["I", "N", "UP", "RUF"]

[tool.mypy]
python_version = "3.11"
check_untyped_defs = true
ignore_missing_imports = true

[tool.pytest.ini_options]
python_files = ["test_*.py", "*_test.py"]
addopts = "--cov=. --cov-report=html --cov-report=term-missing"
```

### **Testing Standards**
```python
# Test naming convention (Both frameworks)
def test_should_create_user_when_valid_data_provided():
    pass

def test_should_return_404_when_user_not_found():
    pass

# Django test example
from django.test import TestCase
from rest_framework.test import APITestCase

class UserAPITestCase(APITestCase):
    def test_should_authenticate_user_with_valid_credentials(self):
        pass

# FastAPI test example
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_should_return_user_profile():
    response = client.get("/api/v1/users/me")
    assert response.status_code == 200
```

---

## 🚨 CONFLICT RESOLUTION: Django vs FastAPI

### **Identified Conflicts & Solutions**

#### 1. **Project Structure Differences**
**Conflict**: Django uses `apps/` directory, FastAPI uses `app/` single directory
**Solution**: Framework detection in AI Agent
```python
# AI Agent detection logic
if os.path.exists('manage.py'):
    framework = 'django'
    structure = 'apps/'
elif os.path.exists('main.py') or 'fastapi' in requirements:
    framework = 'fastapi'  
    structure = 'app/'
```

#### 2. **Testing Framework Differences**
**Conflict**: Django uses `django.test.TestCase`, FastAPI uses pure `pytest`
**Solution**: Framework-specific test templates
```python
# Django testing
from django.test import TestCase
from rest_framework.test import APITestCase

# FastAPI testing  
from fastapi.testclient import TestClient
import pytest
```

#### 3. **Dependency Management**
**Conflict**: Django typically uses `requirements.txt`, FastAPI often uses `pyproject.toml`
**Solution**: Support both formats
```bash
# Detection logic
if [ -f "pyproject.toml" ]; then
    poetry install
elif [ -f "requirements/base.txt" ]; then  
    pip install -r requirements/base.txt
fi
```

---

## 🎯 PROJECT-SPECIFIC CONFIGURATION SECTION

> **Note**: This section contains LocalMind-MCP specific configurations and will be replaced with project-specific content in future projects.

### **LocalMind-MCP Specific Rules**
- MCP protocol implementation in `mcp/` directory
- Local LLM integration (Ollama, LM Studio)
- DeepSeek R1 model with thinking reasoning support
- Docker network configuration for `host.docker.internal`

### **Current Technical Stack**
- **Framework**: Django 4.2.23
- **Database**: PostgreSQL with Redis
- **Authentication**: JWT with djangorestframework-simplejwt
- **AI Services**: OpenAI, Anthropic, Google Generative AI
- **Local LLM**: Ollama, LM Studio integration
- **Testing**: pytest-django with factory_boy

---

## 📈 SUCCESS METRICS

A project following this framework should achieve:
- ✅ **100% Docker-based development** - No host machine execution
- ✅ **>90% test coverage** - Comprehensive testing suite  
- ✅ **English-only Git history** - Professional commit standards
- ✅ **Automated progress tracking** - Self-updating documentation
- ✅ **Function-based milestones** - Clear rollback points
- ✅ **Framework flexibility** - Django & FastAPI support

---

**Remember**: This framework is battle-tested from real project development. Every rule prevents specific production issues. Follow strictly for professional, maintainable applications.