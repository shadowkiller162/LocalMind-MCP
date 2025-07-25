# CLAUDE.md - AI Agent Development Framework

> **Purpose**: Universal development rules and guidelines for Claude Code CLI  
> **Scope**: Django & FastAPI projects  
> **Version**: v2.1  
> **Last Updated**: 2025-07-25

---

## 🚨 AI PREFLIGHT CHECKLIST SYSTEM

> **Critical**: Execute this checklist BEFORE ANY code/file modification to prevent violations and ensure compliance with development standards.

### **⚡ MANDATORY PREFLIGHT CHECKS**

#### 1. **📋 File Strategy Validation**
```
BEFORE MODIFYING/CREATING ANY FILE:
□ Can I modify existing file instead of creating new one?
□ Which files import/reference this module? (Check: grep -r "import.*[filename]" .)
□ Will this modification break existing functionality?
□ Is this the minimal change approach?

❌ VIOLATION DETECTED → Stop and ask human before proceeding
✅ ALL CHECKS PASS → Continue with modification
```

#### 2. **🐳 Docker Environment Compliance**
```
BEFORE EXECUTING ANY COMMAND:
□ Am I using `docker compose exec [service]` prefix?
□ Am I avoiding direct host commands (python, pytest, etc.)?
□ Is the correct service container specified?

❌ VIOLATION DETECTED → Stop and ask human before proceeding
✅ ALL CHECKS PASS → Continue with command execution
```

#### 3. **📋 Documentation Standards**
```
BEFORE CREATING/UPDATING DOCUMENTATION:
□ Did I search for existing documentation files first?
□ Am I updating existing files rather than creating new ones?
□ Are my Git commit messages in English only?

❌ VIOLATION DETECTED → Stop and ask human before proceeding
✅ ALL CHECKS PASS → Continue with documentation update
```

### **📊 PROJECT-SPECIFIC CONSTRAINTS**

#### **Current Project Context: LocalMind-MCP**
```yaml
framework: Django
key_files:
  - ai_agent_automation.py    # Main automation orchestrator
  - progress_updater.py       # Documentation updater
  - test_result_parser.py     # Test result processor
  - framework_detection.py   # Framework detection logic

critical_dependencies:
  - "ai_agent_automation.py:21 → from test_result_parser import TestResultParser"
  - "progress_updater.py:15 → from progress_updater import TestResults"
  
test_command: "docker compose exec django pytest"
docker_service: "django"
```

### **🤖 AI DECISION PROTOCOL**

When ANY modification is needed, AI MUST explicitly state:

```markdown
🔍 PREFLIGHT CHECK EXECUTED:
- File Strategy: [✅ PASS/❌ FAIL - specific reason]
- Docker Compliance: [✅ PASS/❌ FAIL - specific reason]  
- Documentation Standards: [✅ PASS/❌ FAIL - specific reason]

📊 IMPACT ANALYSIS:
- Files affected: [list all files that will be modified]
- Dependencies broken: [list any import/reference breaks]
- Risk level: [HIGH/MEDIUM/LOW]

💡 SOLUTION OPTIONS:
- Option A: [minimal change approach with justification]
- Option B: [alternative approach with trade-offs]
- Recommended: [chosen option with detailed reasoning]

🎯 HUMAN CONSULTATION REQUIRED: [YES/NO - if YES, explain why]
```

### **🚀 EXECUTION TRIGGER MECHANISMS**

#### **1. Session Initialization Trigger**
At the start of EVERY Claude Code session, AI MUST load and acknowledge:

```markdown
🤖 AI AGENT INITIALIZED
📋 Loaded: CLAUDE.md Preflight Checklist System v2.1
🎯 Mode: Human-Assisted Development (HAD)
✅ Ready to assist with rule-compliant development

Current Project Context Loaded:
- Framework: Django
- Docker Service: django  
- Key Dependencies: [list from PROJECT-SPECIFIC CONSTRAINTS]
```

#### **2. Pre-Modification Trigger**
BEFORE any file modification, AI MUST:

```markdown
⚠️  PREFLIGHT CHECK REQUIRED
I'm about to modify [filename]. Let me run the mandatory checks first...

[Execute checklist and display results]

🤔 HUMAN DECISION POINT:
Based on the above analysis, would you like me to:
A) Proceed with recommended approach
B) Use alternative approach  
C) Let you handle this manually
D) Discuss other options

Please select: [A/B/C/D]
```

#### **3. Violation Detection Trigger**
When violations are detected:

```markdown
🚨 RULE VIOLATION DETECTED

Violation Type: [specific rule broken]
Potential Impact: [consequences if ignored]
Compliant Alternative: [suggested solution]

🤔 HUMAN CHOICE REQUIRED:
1. Apply compliant solution automatically
2. Override violation with justification
3. Pause for manual handling
4. Update rule (if this is a new valid pattern)

Please respond with choice number: [1/2/3/4]
```

#### **4. Learning Feedback Trigger**
After human corrections or overrides:

```markdown
📚 LEARNING OPPORTUNITY DETECTED

Human Action: [what you did differently]
AI Suggestion: [what AI recommended]
Outcome: [result of human choice]

🎯 RULE UPDATE PROPOSAL:
Should this pattern be added to CLAUDE.md for future reference?
- New rule: [proposed addition]  
- Reason: [why this improves development]

Add to checklist? [Yes/No/Modify]
```

### **⚡ IMMEDIATE ACTIVATION PROTOCOL**

To activate this system immediately, add this section to your Claude Code CLI startup prompt:

```markdown
## SYSTEM INITIALIZATION COMMAND
Load and execute CLAUDE.md Preflight Checklist System v2.1
- Enable Human-Assisted Development (HAD) mode
- Display session initialization trigger
- Prepare to execute preflight checks before any modification
- Ready violation detection and human consultation triggers
```

### **🔄 TRIGGER TESTING PROTOCOL**

To verify the system works correctly:

```markdown
TEST SEQUENCE:
1. Start new Claude Code session → Should display initialization trigger
2. Request file modification → Should execute preflight check
3. Introduce intentional violation → Should trigger violation detection
4. Provide feedback/correction → Should trigger learning feedback

PASS CRITERIA:
- All 4 triggers execute correctly
- Human decision points are clearly presented  
- No actions taken without human confirmation on violations
```

### **🚨 VIOLATION RESPONSE PROTOCOL**

When violations are detected:

#### **For HIGH RISK Changes:**
- ❌ **STOP IMMEDIATELY**
- 🤔 **Ask Human**: "I detected [violation type]. This could [potential impact]. Should I proceed with [alternative approach] or would you prefer a different solution?"

#### **For MEDIUM RISK Changes:**
- ⚠️ **Warn and Suggest**: "I notice this violates [rule]. I recommend [compliant alternative]. Shall I proceed with the compliant approach?"

#### **For LOW RISK Changes:**
- ✅ **Proceed with Note**: "Applied [compliant solution] to avoid [potential violation]."

### **📈 EFFECTIVENESS METRICS**

Track these metrics to measure system improvement:

```yaml
token_efficiency:
  baseline_tokens: "[record initial session token usage]"
  optimized_tokens: "[record post-checklist token usage]"
  target_reduction: "30%"

file_management:
  duplicate_files_created: 0
  unnecessary_modifications: 0
  backward_compatibility_breaks: 0

human_intervention:
  violations_caught_pre_execution: "[count]"
  human_corrections_required: "[count]" 
  error_types_prevented: "[list categories]"

quality_indicators:
  import_dependency_errors: 0
  architecture_violations: 0
  rule_compliance_rate: ">95%"
```

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