# CLAUDE.md - AI Agent Development Framework

> **Purpose**: Universal development rules and guidelines for Claude Code CLI  
> **Scope**: Django & FastAPI projects  
> **Version**: v2.3  
> **Last Updated**: 2025-07-28

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

#### 2. **🐳 Docker-Host Environment Boundary Compliance**
```
BEFORE EXECUTING ANY COMMAND - Validate execution context:

DOCKER CONTAINER COMMANDS (use `docker compose exec [service]`):
□ Application runtime: python manage.py, pytest, uvicorn
□ Database operations: migrate, shell, dbshell
□ Static files: collectstatic, compress
□ Package management: pip install (within requirements workflow)

HOST ENVIRONMENT COMMANDS (execute directly on host):
□ Version control: git add, commit, push, pull, status, log
□ Git configuration: git config --global user.name/email
□ File system operations: file creation/editing with IDE
□ SSH operations: ssh-keygen, ssh connections
□ Development tool configuration: IDE settings, shell configuration

❌ VIOLATION EXAMPLES:
- docker compose exec django git commit (Git in container)
- python manage.py migrate (Direct host execution of app commands)
- docker compose exec django git config user.email (Git config in container)

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

#### 4. **🔗 Import Dependency Validation**
```
BEFORE WRITING/MODIFYING IMPORT STATEMENTS:
□ Does the imported module actually exist? (Check: find . -name "[module].py")
□ Is the import path correct based on actual file structure?
□ Are all required types/classes available in the target module?
□ Will this import work in the actual runtime environment?

❌ VIOLATION DETECTED → Stop and verify module structure before proceeding
✅ ALL CHECKS PASS → Continue with import modification
```

#### 5. **🎯 AI Response Content Parsing**
```
BEFORE PROCESSING AI/LLM RESPONSES:
□ Does the response contain raw thinking tags (<think>, <thinking>)?
□ Are thinking processes properly separated from user-facing content?
□ Is the content human-readable and properly formatted?
□ Will the content render correctly in templates?

❌ VIOLATION DETECTED → Parse and clean response content before display
✅ ALL CHECKS PASS → Continue with response rendering
```

#### 6. **🔤 UTF-8 Encoding Compliance**
```
BEFORE RETURNING HTTP RESPONSES:
□ Are all .content.decode() calls using explicit 'utf-8' encoding?
□ Are JsonResponse calls using ensure_ascii=False parameter?
□ Will Chinese/Unicode characters display correctly in frontend?
□ Are template render outputs properly encoded?

❌ VIOLATION DETECTED → Add explicit UTF-8 encoding parameters
✅ ALL CHECKS PASS → Continue with response rendering
```

#### 7. **🎨 Template Content Optimization**
```
BEFORE MODIFYING TEMPLATE FILES:
□ Are JavaScript functions duplicated across templates?
□ Is static content (CSS/JS) loaded in main template instead of partials?
□ Will this template generate excessive HTML when rendered multiple times?
□ Are there unnecessary whitespace or repeated code blocks?

❌ VIOLATION DETECTED → Consolidate repeated content to main template
✅ ALL CHECKS PASS → Continue with template modification
```

#### 8. **🔄 Frontend Integration Protocol Compliance**
```
BEFORE IMPLEMENTING FRONTEND RESPONSES:
□ Does HTMX configuration expect HTML or JSON response?
□ Are response types consistent with frontend expectations?
□ Will the response format render correctly in the target element?
□ Is the response content type properly set (text/html vs application/json)?

❌ VIOLATION DETECTED → Align response format with frontend protocol
✅ ALL CHECKS PASS → Continue with response implementation
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
  - "mcp_management/views.py → from mcp.llm import UnifiedModelManager, LLMServiceType"
  - "mcp_management/views.py → from mcp.llm.types import ChatRequest, ChatMessage"

mcp_module_structure:
  - "mcp/llm/__init__.py → UnifiedModelManager, LLMServiceType exports"
  - "mcp/llm/types.py → ChatRequest, ChatMessage dataclasses"
  - "mcp/llm/unified_manager.py → UnifiedModelManager class implementation"
  - "❌ NEVER import: mcp.llm_client (does not exist)"

ai_response_parsing:
  - "views.py:parse_ai_response() → Separates <think> tags from content"
  - "templates/partials/chat_message.html → message-text class for formatting"
  - "static/components/ai_chat.css → Enhanced message text styling"
  - "✅ ALWAYS parse: Raw AI responses before template rendering"
  - "❌ NEVER display: Unparsed content with thinking tags"

utf8_encoding_standards:
  - "views.py → .content.decode('utf-8') for all template renders"
  - "views.py → JsonResponse(..., json_dumps_params={'ensure_ascii': False})"
  - "✅ ALWAYS use: Explicit UTF-8 encoding for Chinese characters"
  - "❌ NEVER use: .content.decode() without encoding parameter"
  - "❌ NEVER allow: Unicode escape sequences in frontend display"

template_optimization_standards:
  - "partials/chat_message.html → No JavaScript code in message templates"
  - "dashboard.html → Central JavaScript function management"
  - "clean_html_whitespace() → Remove excessive whitespace/newlines"
  - "✅ ALWAYS consolidate: Repeated JavaScript/CSS in main template"
  - "❌ NEVER duplicate: Static content across partial templates"

frontend_integration_protocols:
  - "HTMX views → Return HttpResponse(html, content_type='text/html')"
  - "API views → Return JsonResponse(..., json_dumps_params={'ensure_ascii': False})"
  - "hx-target + hx-swap → Expects direct HTML insertion"
  - "✅ ALWAYS match: Response format with frontend expectations"
  - "❌ NEVER return: JSON to HTMX expecting HTML"
  
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

## 🎯 PROJECT DEVELOPMENT GUIDANCE PRINCIPLES

> **Purpose**: Framework-agnostic development guidance derived from real project experience  
> **Scope**: Advisory principles for Django & FastAPI projects  
> **Usage**: Reference for decision-making, not mandatory rules

### **🔍 1. User Need Reality Analysis**

**Principle**: Always question the real need behind technical requests

```markdown
Decision Pattern:
- User request: "I want [Technology X]"
- Real analysis: "I need [Business Outcome Y]"
- Solution evaluation: Can simpler approaches achieve Y?

Example Applications:
- Streaming request → Status visibility need → Enhanced UI feedback
- Real-time features → Immediate response need → Optimistic UI updates
- Complex animations → Professional feel need → Subtle, purposeful transitions
```

**Framework Application:**
- **Django**: Leverage HTMX events for immediate UI feedback
- **FastAPI**: Use WebSocket judiciously, prefer HTTP + rich frontend states

### **🏗️ 2. Progressive Enhancement Strategy**

**Principle**: Maximize user experience improvement with minimal architectural risk

```markdown
Enhancement Priority Matrix:
1. Frontend optimization (High impact, low risk)
2. API response enrichment (Medium impact, low risk)  
3. Backend optimization (Medium impact, medium risk)
4. Architecture changes (Variable impact, high risk)

Decision Framework:
- Can frontend changes solve 80% of the user experience problem?
- Does the current API provide sufficient data for enhancement?
- Will existing architecture support the enhancement long-term?
```

**Framework Application:**
- **Django**: Enhance templates and static assets before changing views
- **FastAPI**: Enrich response models before adding new endpoints

### **⚡ 3. Frontend-Backend Separation for UX Enhancement**

**Principle**: Solve UX problems at the appropriate layer

```markdown
Problem Classification:
- UI Responsiveness → Frontend solution (state management, optimistic updates)
- Data Processing Speed → Backend solution (caching, optimization)
- Perceived Performance → Frontend solution (progress indicators, transitions)
- Actual Performance → Backend solution (query optimization, architecture)

Implementation Strategy:
- Keep backend APIs stable and predictable
- Build rich interactions in frontend layer
- Use existing event systems rather than adding new communication channels
```

**Framework Application:**
- **Django**: Utilize HTMX events, Django template context
- **FastAPI**: Leverage Pydantic models, JavaScript frontend frameworks

### **👁️ 4. User State Visibility Design Pattern**

**Principle**: Make system state always visible to users during any waiting period

```markdown
Required State Communication:
1. Acknowledgment: "Your request is received"
2. Progress: "Here's what's happening"  
3. Estimation: "Here's how long it might take"
4. Completion: "Here's your result"
5. Recovery: "Here's what to do if something goes wrong"

Implementation Template:
- Pre-request: Immediate UI state change
- During-request: Progress indication + time estimation
- Post-request: Result display + state restoration
- Error-handling: Clear error communication + recovery options
```

**Framework Application:**
- **Django**: Use HTMX events + Django messages framework
- **FastAPI**: Use HTTP status codes + rich error responses

### **💰 5. Technology Choice Cost-Benefit Framework**

**Principle**: Evaluate new technology adoption against clear criteria

```markdown
Evaluation Matrix:
                    | Implementation | Maintenance | User Benefit | Risk Level |
--------------------|----------------|-------------|--------------|------------|
Current + Enhancement|     Low        |    Low      |    High      |    Low     |
New Architecture    |     High       |    High     |   Variable   |    High    |

Decision Criteria:
- User benefit must be 3x the implementation cost for architectural changes
- Maintenance burden must be justified by long-term value
- Risk level must align with project stage and team capacity
```

**Framework Application:**
- **Django**: Consider django-htmx before WebSockets, enhance ModelForms before custom APIs
- **FastAPI**: Consider rich frontend states before WebSockets, enhance Pydantic before custom serialization

### **🔄 6. Standardized State Management Pattern**

**Principle**: Consistent state management improves user experience and code maintainability

```markdown
Component State Standards:
- Visual states: ready, processing, completed, error
- Functional states: enabled, disabled, loading
- Informational states: progress, estimation, feedback

Implementation Requirements:
- State transitions must be visually clear
- Error states must provide recovery options  
- Loading states must prevent duplicate actions
- Completion states must guide next actions
```

**Framework Application:**
- **Django**: Use CSS classes + HTMX attributes for state management
- **FastAPI**: Use HTTP status codes + frontend state management libraries

### **📊 7. Performance Impact Pre-Assessment**

**Principle**: Define and measure performance impact before implementing enhancements

```markdown
Assessment Categories:
- Resource consumption (bundle size, memory usage)
- Runtime performance (animation smoothness, response times)
- User experience metrics (perceived speed, interaction delays)
- Maintainability impact (code complexity, debugging difficulty)

Measurement Standards:
- Frontend additions: Document size increases and performance impact
- Backend changes: Measure response time and resource usage changes
- User experience: Define measurable improvement criteria
```

**Framework Application:**
- **Django**: Use Django Debug Toolbar, monitor static file sizes
- **FastAPI**: Use built-in profiling, monitor response times

### **🚀 IMPLEMENTATION GUIDELINES**

#### **When to Apply These Principles:**
- ✅ During feature planning and technical design
- ✅ When evaluating user experience improvements
- ✅ Before adopting new technologies or patterns
- ✅ During code review and architecture discussions

#### **When NOT to Apply:**
- ❌ As rigid rules that override project-specific needs
- ❌ In emergency bug fixes or critical security updates
- ❌ When client/stakeholder requirements explicitly override UX considerations
- ❌ In early prototype stages where rapid iteration is prioritized

#### **Framework-Specific Adaptations:**

**Django Projects:**
- Leverage Django's built-in admin, forms, and template system
- Use HTMX for enhanced interactivity before considering SPA frameworks
- Apply these principles within Django's "batteries included" philosophy

**FastAPI Projects:**  
- Leverage Pydantic for rich data validation and serialization
- Use FastAPI's automatic API documentation as part of user experience
- Apply these principles within FastAPI's performance-first approach

### **📈 SUCCESS METRICS**

Track the effectiveness of these principles through:
- User experience improvements (measured through user feedback, usage analytics)
- Development velocity (feature delivery speed, bug reduction)
- Code maintainability (review time, onboarding speed)
- Technical debt management (refactoring frequency, architecture stability)

---

**Remember**: These are guidance principles derived from real project experience. Adapt them to your specific project context, team capabilities, and user needs.

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

### 4. **📦 Docker Dependency Management Protocol**
```bash
# ✅ REQUIRED - Proper Docker dependency workflow
# Step 1: Update requirements file
echo "django-htmx==1.17.2" >> requirements/base.txt
# Step 2: Rebuild Docker image
docker compose build django
# Step 3: Restart services
docker compose up django -d

# ❌ FORBIDDEN - Direct container package installation
docker compose exec django pip install django-htmx==1.17.2
docker exec container_name pip install package_name

# 🚨 CRITICAL RULE: Container-installed packages disappear on restart
# Always use requirements files + image rebuild for persistent dependencies
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