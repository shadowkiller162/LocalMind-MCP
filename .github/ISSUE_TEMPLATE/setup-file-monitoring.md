---
name: Infrastructure - File Size Monitoring
about: Setup automated file size monitoring and pre-commit hooks
title: 'chore: Setup file size monitoring and pre-commit hooks'
labels: 'infrastructure, automation, code-quality'
assignees: ''
---

## 📋 問題描述

**當前狀態：**
- ❌ 無自動化文件大小檢查
- ❌ 無 pre-commit hooks 防止超標代碼提交
- ❌ 無定期掃描和報告機制
- ⚠️ 已發現 5 個文件嚴重超標

**需求背景：**
根據 [CLAUDE.md](../../CLAUDE.md) Linus 方法論和代碼分析報告：
- 需要預防性監控（防止新的超標文件產生）
- 需要持續追蹤（監控現有超標文件的改善情況）
- 需要自動化檢查（減少人工審查負擔）

**核心問題：**
```
【品味評分】
🔴 基礎設施缺失 - 沒有預防機制，技術債會持續累積

【問題】
- 開發者不知道文件何時超標
- 沒有 CI/CD 檢查防止超標代碼合併
- 無法追蹤技術債改善趨勢
```

## 🎯 實施目標

**可測量指標：**
- ✅ Pre-commit hook 攔截超標文件提交
- ✅ CI/CD 自動檢查文件大小
- ✅ 每週生成技術債報告
- ✅ 可視化趨勢追蹤

**預期工具鏈：**
```
開發階段：
├── pre-commit hook (本地檢查)
├── VS Code 插件提示
└── Git commit 自動掃描

CI/CD 階段：
├── GitHub Actions (自動檢查)
├── Pull Request 狀態檢查
└── 自動評論超標警告

監控階段：
├── 定期掃描腳本
├── 技術債報告生成
└── Slack/Discord 通知
```

## 🔧 實作步驟

### Phase 1: Pre-commit Hook 設置

**步驟 1.1: 安裝 pre-commit 框架**
更新 `requirements/local.txt`：
```txt
# Code Quality Tools
pre-commit==3.5.0
radon==6.0.1  # 複雜度檢查
```

**步驟 1.2: 創建 pre-commit 配置**
創建 `.pre-commit-config.yaml`：
```yaml
repos:
  # File size check
  - repo: local
    hooks:
      - id: check-file-size
        name: Check Python file size (<300 lines)
        entry: python scripts/checks/check_file_size.py
        language: python
        files: \.py$
        exclude: ^(migrations|staticfiles|tests)/

  # Complexity check
  - repo: local
    hooks:
      - id: check-complexity
        name: Check code complexity (CC <=10)
        entry: radon cc --min C --total-average
        language: python
        files: \.py$
        exclude: ^(migrations|staticfiles|tests)/

  # Function length check
  - repo: local
    hooks:
      - id: check-function-length
        name: Check function length (<50 lines)
        entry: python scripts/checks/check_function_length.py
        language: python
        files: \.py$
        exclude: ^(migrations|staticfiles)/

  # Standard quality checks
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [django-stubs, djangorestframework-stubs]
```

**步驟 1.3: 創建文件大小檢查腳本**
創建 `scripts/checks/check_file_size.py`：
```python
#!/usr/bin/env python3
"""
Pre-commit hook: Check Python file size

Enforces Linus methodology file size limits:
- Files: <300 lines
- Classes: <200 lines (checked separately)
"""
import sys
from pathlib import Path

MAX_FILE_LINES = 300
EXCLUDE_PATTERNS = ['migrations/', 'staticfiles/', '__pycache__/']


def check_file_size(file_path: Path) -> tuple[bool, int]:
    """Check if file exceeds size limit

    Returns:
        Tuple[is_valid, line_count]
    """
    # Check exclusions
    if any(pattern in str(file_path) for pattern in EXCLUDE_PATTERNS):
        return True, 0

    # Count lines
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = len(f.readlines())
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False, 0

    # Check limit
    if lines > MAX_FILE_LINES:
        return False, lines

    return True, lines


def main():
    """Main check function"""
    files_to_check = sys.argv[1:]
    if not files_to_check:
        return 0

    failed_files = []

    print("🔍 Checking file sizes (Linus methodology: <300 lines)...")

    for file_path in files_to_check:
        path = Path(file_path)
        if not path.suffix == '.py':
            continue

        is_valid, line_count = check_file_size(path)

        if not is_valid:
            failed_files.append((file_path, line_count))
            print(f"❌ {file_path}: {line_count} lines (limit: {MAX_FILE_LINES})")
        else:
            print(f"✅ {file_path}: {line_count} lines")

    if failed_files:
        print("\n" + "="*60)
        print("🚨 COMMIT BLOCKED: File size violations detected!")
        print("="*60)
        print("\nFiles exceeding 300 line limit:")
        for file_path, line_count in failed_files:
            excess = line_count - MAX_FILE_LINES
            print(f"  - {file_path}: {line_count} lines (+{excess} over limit)")

        print("\n📋 Please refactor these files before committing.")
        print("See CLAUDE.md for refactoring guidelines.")
        return 1

    print("\n✅ All files pass size check!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

**步驟 1.4: 創建函數長度檢查腳本**
創建 `scripts/checks/check_function_length.py`：
```python
#!/usr/bin/env python3
"""
Pre-commit hook: Check function length

Enforces Linus methodology function size limits:
- Functions: <50 lines
- Most functions should be <20 lines
"""
import ast
import sys
from pathlib import Path
from typing import List, Tuple

MAX_FUNCTION_LINES = 50
EXCLUDE_PATTERNS = ['migrations/', 'staticfiles/', 'tests/']


class FunctionLengthChecker(ast.NodeVisitor):
    """AST visitor to check function lengths"""

    def __init__(self, filename: str):
        self.filename = filename
        self.violations: List[Tuple[str, int, int]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definition"""
        start_line = node.lineno
        end_line = node.end_lineno or start_line
        length = end_line - start_line + 1

        if length > MAX_FUNCTION_LINES:
            self.violations.append((node.name, start_line, length))

        self.generic_visit(node)


def check_file(file_path: Path) -> List[Tuple[str, int, int]]:
    """Check all functions in a file

    Returns:
        List of (function_name, line_number, length) tuples
    """
    # Check exclusions
    if any(pattern in str(file_path) for pattern in EXCLUDE_PATTERNS):
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(file_path))

        checker = FunctionLengthChecker(str(file_path))
        checker.visit(tree)
        return checker.violations

    except Exception as e:
        print(f"⚠️  Could not parse {file_path}: {e}")
        return []


def main():
    """Main check function"""
    files_to_check = sys.argv[1:]
    if not files_to_check:
        return 0

    all_violations = []

    print("🔍 Checking function lengths (Linus methodology: <50 lines)...")

    for file_path in files_to_check:
        path = Path(file_path)
        if not path.suffix == '.py':
            continue

        violations = check_file(path)
        if violations:
            all_violations.extend([(file_path, *v) for v in violations])

    if all_violations:
        print("\n" + "="*60)
        print("🚨 COMMIT BLOCKED: Function length violations detected!")
        print("="*60)
        print("\nFunctions exceeding 50 line limit:")
        for file_path, func_name, line_no, length in all_violations:
            excess = length - MAX_FUNCTION_LINES
            print(f"  - {file_path}:{line_no} - {func_name}() = {length} lines (+{excess})")

        print("\n📋 Please refactor these functions before committing.")
        print("💡 Tip: Most functions should be <20 lines, 50 is the absolute maximum.")
        return 1

    print("\n✅ All functions pass length check!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

### Phase 2: GitHub Actions CI/CD 整合

**步驟 2.1: 創建 CI workflow**
創建 `.github/workflows/code-quality.yml`：
```yaml
name: Code Quality Checks

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  file-size-check:
    name: File Size Check
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install radon

      - name: Check file sizes
        run: |
          python scripts/checks/check_file_size.py $(find . -name "*.py" ! -path "*/migrations/*" ! -path "*/staticfiles/*")

      - name: Check function lengths
        run: |
          python scripts/checks/check_function_length.py $(find . -name "*.py" ! -path "*/migrations/*" ! -path "*/tests/*")

      - name: Check code complexity
        run: |
          radon cc --min C --total-average $(find . -name "*.py" ! -path "*/migrations/*" ! -path "*/staticfiles/*")

  technical-debt-report:
    name: Generate Technical Debt Report
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'

    steps:
      - uses: actions/checkout@v4

      - name: Generate report
        run: |
          python scripts/checks/generate_debt_report.py > debt-report.md

      - name: Comment on PR
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('debt-report.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: report
            });
```

### Phase 3: 技術債報告生成

**步驟 3.1: 創建報告生成腳本**
創建 `scripts/checks/generate_debt_report.py`：
```python
#!/usr/bin/env python3
"""
Generate Technical Debt Report

Scans codebase and generates a report of:
- Files exceeding size limits
- Functions exceeding length limits
- High complexity code
- Trends over time
"""
import subprocess
from pathlib import Path
from datetime import datetime


def scan_file_sizes():
    """Scan all Python files for size violations"""
    violations = []
    for py_file in Path('.').rglob('*.py'):
        if 'migrations' in str(py_file) or 'staticfiles' in str(py_file):
            continue

        lines = len(py_file.read_text().splitlines())
        if lines > 300:
            violations.append((str(py_file), lines))

    return sorted(violations, key=lambda x: x[1], reverse=True)


def generate_report():
    """Generate markdown report"""
    violations = scan_file_sizes()

    report = f"""## 📊 Technical Debt Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Standard:** Linus Methodology (CLAUDE.md)

### 🔴 File Size Violations

**Limit:** 300 lines
**Found:** {len(violations)} violations

"""

    if violations:
        report += "| File | Lines | Excess |\n"
        report += "|------|-------|--------|\n"
        for file_path, lines in violations:
            excess = lines - 300
            report += f"| `{file_path}` | {lines} | +{excess} |\n"
    else:
        report += "✅ **No violations found!**\n"

    report += "\n---\n"
    report += "\n📋 **Action Required:** Please refactor files exceeding 300 lines.\n"
    report += "📚 **Reference:** See [CLAUDE.md](../../CLAUDE.md) for guidelines.\n"

    return report


if __name__ == '__main__':
    print(generate_report())
```

## ✅ 驗收標準

### 基礎設施
- [ ] pre-commit hooks 已安裝並運作
- [ ] GitHub Actions workflow 已設置
- [ ] 檢查腳本正常執行
- [ ] 報告生成功能正常

### 功能驗證
- [ ] 超標文件無法提交（pre-commit 攔截）
- [ ] PR 自動檢查文件大小
- [ ] PR 自動生成技術債報告
- [ ] CI/CD 檢查失敗時 PR 無法合併

### 文檔更新
- [ ] README 添加 pre-commit 安裝說明
- [ ] CONTRIBUTING 添加代碼品質標準
- [ ] CI/CD 狀態徽章添加到 README

## 📊 預期收益

**預防機制：**
- ✅ 100% 攔截新的超標代碼
- ✅ 開發者即時反饋
- ✅ PR 審查自動化

**可見性提升：**
- ✅ 每週技術債報告
- ✅ 趨勢追蹤
- ✅ 改善進度可視化

## 📚 參考文檔

- [CLAUDE.md - Linus 方法論](../../CLAUDE.md)
- [Pre-commit 官方文檔](https://pre-commit.com/)
- [GitHub Actions 文檔](https://docs.github.com/actions)

## 🏷️ 標籤

`infrastructure` `automation` `code-quality` `ci-cd` `prevention`

## ⏱️ 預估工時

**2 天**

**分解：**
- Day 1: Pre-commit hooks + 檢查腳本
- Day 2: GitHub Actions + 報告生成
