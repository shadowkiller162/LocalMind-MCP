---
name: Code Refactoring - test_result_parser.py
about: Refactor test result parser following Linus methodology (661 lines → <300 lines)
title: 'refactor: Split test_result_parser.py into framework-specific parsers'
labels: 'refactoring, technical-debt, high-priority, testing'
assignees: ''
---

## 📋 問題描述

**當前狀態：**
- 文件：`scripts/test_result_parser.py`
- 行數：661 / 300（超標 2.2 倍）🔴 **全專案最大文件**
- 類別數量：2 個主要類 (`TestResultParser`, `CoverageReportParser`)
- 方法數量：TestResultParser 有 17 個方法

**違反規範：**
根據 [CLAUDE.md](../../CLAUDE.md) Linus 方法論：
- ❌ 文件行數嚴重超標（661 / 300）
- ❌ TestResultParser 類別職責過多（17個方法）
- ❌ 職責混亂：pytest解析 + Django測試解析 + 覆蓋率報告 + 命令執行

**核心問題：**
```
【品味評分】
🔴 垃圾 - 661行的"解析器"？這是個該死的測試框架！

【致命問題】
- TestResultParser 有 17 個方法？一個類做 17 件事？
- 把測試解析、覆蓋率報告、命令執行全塞一個文件了
- 真正的問題：職責邊界不清晰 → 難以測試 → 難以維護 → 技術債爆炸
```

## 🎯 重構目標

**可測量指標：**
- ✅ 所有文件 < 150 行
- ✅ 所有類別 < 200 行
- ✅ 每個類別職責單一
- ✅ 擴展性：新增測試框架只需新增一個文件

**預期結構：**
```
scripts/parsers/
├── __init__.py (30 行) - 統一導出 + Facade
├── base_parser.py (100 行)
│   └── BaseTestParser (抽象基類)
├── pytest_parser.py (150 行)
│   └── PytestParser (pytest 專用)
├── django_parser.py (120 行)
│   └── DjangoTestParser (Django 測試專用)
├── unittest_parser.py (100 行)
│   └── UnittestParser (unittest 專用)
├── coverage_parser.py (120 行)
│   └── CoverageReportParser (覆蓋率報告)
└── command_executor.py (100 行)
    └── TestCommandExecutor (命令執行邏輯)
```

## 🔧 實作步驟

### Phase 1: 建立基礎架構（不破壞現有功能）

**步驟 1.1: 創建解析器目錄結構**
```bash
mkdir -p scripts/parsers
touch scripts/parsers/__init__.py
```

**步驟 1.2: 創建抽象基類**
創建 `parsers/base_parser.py`：
```python
"""測試結果解析器基類"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional
from progress_updater import TestResults


@dataclass
class ParseResult:
    """解析結果統一格式"""
    passed: int
    failed: int
    skipped: int
    errors: int
    duration: float
    coverage: Optional[float] = None


class BaseTestParser(ABC):
    """測試結果解析器抽象基類"""

    @abstractmethod
    def can_parse(self, output: str) -> bool:
        """判斷是否可以解析此輸出"""
        pass

    @abstractmethod
    def parse(self, output: str) -> ParseResult:
        """解析測試輸出"""
        pass

    @abstractmethod
    def extract_failures(self, output: str) -> List[str]:
        """提取失敗測試列表"""
        pass
```

### Phase 2: 按框架拆分解析器

**步驟 2.1: 創建 pytest 解析器**
創建 `parsers/pytest_parser.py`：
```python
"""Pytest 測試結果解析器"""
import re
from typing import List
from .base_parser import BaseTestParser, ParseResult


class PytestParser(BaseTestParser):
    """Pytest 專用解析器"""

    # 保留原有的 PYTEST_PATTERNS
    PYTEST_PATTERNS = {
        'summary': [
            r'=+ (\d+) failed,? (\d+) passed.*in ([\d.]+)s =+',
            r'=+ (\d+) passed.*in ([\d.]+)s =+',
        ],
        'coverage': [
            r'TOTAL\s+(\d+)\s+(\d+)\s+(\d+)%',
        ],
        'slow_tests': [
            r'([\d.]+)s call.*::(test_\w+)',
        ]
    }

    def can_parse(self, output: str) -> bool:
        """檢查是否為 pytest 輸出"""
        return 'pytest' in output.lower() or '=== test session starts ===' in output

    def parse(self, output: str) -> ParseResult:
        """解析 pytest 輸出

        移動原有 _parse_pytest_summary 邏輯到這裡
        """
        pass

    def extract_failures(self, output: str) -> List[str]:
        """提取失敗的測試"""
        pass
```

**步驟 2.2: 創建 Django 測試解析器**
創建 `parsers/django_parser.py`：
```python
"""Django 測試結果解析器"""
from .base_parser import BaseTestParser, ParseResult


class DjangoTestParser(BaseTestParser):
    """Django 測試專用解析器"""

    DJANGO_PATTERNS = {
        'summary': [
            r'Ran (\d+) tests? in ([\d.]+)s',
            r'FAILED \(failures=(\d+)(?:, errors=(\d+))?\)',
        ]
    }

    def can_parse(self, output: str) -> bool:
        """檢查是否為 Django 測試輸出"""
        return 'Ran' in output and 'test' in output

    def parse(self, output: str) -> ParseResult:
        """解析 Django 測試輸出"""
        pass
```

**步驟 2.3: 創建 unittest 解析器**
創建 `parsers/unittest_parser.py`：
```python
"""Unittest 測試結果解析器"""
from .base_parser import BaseTestParser, ParseResult


class UnittestParser(BaseTestParser):
    """Unittest 專用解析器"""

    def can_parse(self, output: str) -> bool:
        """檢查是否為 unittest 輸出"""
        return 'unittest' in output.lower()

    def parse(self, output: str) -> ParseResult:
        """解析 unittest 輸出"""
        pass
```

### Phase 3: 提取獨立功能模組

**步驟 3.1: 創建覆蓋率解析器**
創建 `parsers/coverage_parser.py`：
```python
"""測試覆蓋率報告解析器"""
import re
from typing import Optional


class CoverageReportParser:
    """覆蓋率報告解析器（保留原有邏輯）"""

    def parse_coverage_report(self, output: str) -> Optional[float]:
        """解析覆蓋率報告"""
        # 移動原有的 CoverageReportParser 邏輯
        pass
```

**步驟 3.2: 創建命令執行器**
創建 `parsers/command_executor.py`：
```python
"""測試命令執行器"""
import subprocess
import time
from pathlib import Path
from typing import Tuple


class TestCommandExecutor:
    """測試命令執行器"""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()

    def execute(self, command: str, timeout: int = 300) -> Tuple[str, int, float]:
        """執行測試命令

        Returns:
            Tuple[output, return_code, execution_time]
        """
        start_time = time.time()

        result = subprocess.run(
            command,
            cwd=self.project_root,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=True
        )

        execution_time = time.time() - start_time
        return result.stdout + result.stderr, result.returncode, execution_time
```

### Phase 4: 向後相容性 Facade

**步驟 4.1: 創建 Facade 包裝**
在 `parsers/__init__.py` 中：
```python
"""測試結果解析器統一接口"""
from .base_parser import BaseTestParser, ParseResult
from .pytest_parser import PytestParser
from .django_parser import DjangoTestParser
from .unittest_parser import UnittestParser
from .coverage_parser import CoverageReportParser
from .command_executor import TestCommandExecutor


class TestResultParser:
    """向後相容的統一解析器（Facade Pattern）"""

    def __init__(self, project_root=None):
        self.project_root = project_root
        self.parsers = [
            PytestParser(),
            DjangoTestParser(),
            UnittestParser(),
        ]
        self.executor = TestCommandExecutor(project_root)
        self.coverage_parser = CoverageReportParser()

    def run_and_parse_tests(self, test_command: str):
        """執行並解析測試（保持原有 API）"""
        # 使用 executor 執行命令
        output, return_code, duration = self.executor.execute(test_command)

        # 自動選擇適合的解析器
        for parser in self.parsers:
            if parser.can_parse(output):
                result = parser.parse(output)
                # 轉換為原有的 TestResults 格式
                return self._convert_to_test_results(result, output, return_code)

        # 如果無法識別，返回原始輸出
        return self._default_result(output, return_code)

    def _convert_to_test_results(self, result, output, return_code):
        """轉換為 TestResults 格式"""
        from progress_updater import TestResults
        return TestResults(
            passed=result.passed,
            failed=result.failed,
            skipped=result.skipped,
            # ... 其他欄位
        )


# 保持向後相容的導出
__all__ = [
    'TestResultParser',
    'CoverageReportParser',
    'BaseTestParser',
]
```

**步驟 4.2: 更新原文件為 Facade**
修改 `scripts/test_result_parser.py`：
```python
#!/usr/bin/env python3
"""
Test Result Parser - Backward Compatibility Facade

此文件保持向後相容性，實際邏輯已移至 parsers/ 目錄。
"""
from parsers import TestResultParser, CoverageReportParser

# 保持原有的導入接口
__all__ = ['TestResultParser', 'CoverageReportParser']
```

## ✅ 驗收標準

### 代碼品質
- [ ] 所有文件 < 150 行
- [ ] 所有類別 < 200 行
- [ ] 每個類別方法數 < 10
- [ ] mypy 檢查通過（0 錯誤）
- [ ] ruff 檢查通過（0 警告）

### 功能測試
- [ ] 所有現有測試通過
- [ ] pytest 解析正確
- [ ] Django 測試解析正確
- [ ] 覆蓋率報告解析正確
- [ ] `ai_agent_automation.py` 正常運作

### 架構檢查
- [ ] 職責單一（一個解析器只處理一種框架）
- [ ] 易於擴展（新增框架只需加一個文件）
- [ ] 無循環依賴
- [ ] 抽象層次清晰

### 向後相容性
- [ ] 現有腳本正常運作（`ai_agent_automation.py`）
- [ ] API 簽名不變
- [ ] 導入路徑保持一致
- [ ] 功能零破壞

## 🔄 回滾計劃

**Git 標籤：** `before-parser-refactor`

**回滾命令：**
```bash
git tag before-parser-refactor  # 重構前打標籤
git reset --hard before-parser-refactor  # 如需回滾
```

**驗證腳本：**
```bash
# 檢查文件大小
find scripts/parsers -name "*.py" -exec wc -l {} +

# 測試解析功能
python scripts/test_result_parser.py -c "docker compose exec django pytest --version" --json

# 檢查自動化腳本
python scripts/ai_agent_automation.py --dry-run
```

## 📊 預期收益

**可測量改進：**
- 最大文件：661 行 → ~150 行 ✅
- 最大類別：17 方法 → ~8 方法 ✅
- 文件數量：1 個 → 7 個（職責清晰）✅
- 技術債等級：🔴 CRITICAL → 🟢 LOW

**長期價值：**
- ✅ 新增測試框架支援：只需加一個 parser 文件
- ✅ 更容易測試：每個 parser 可獨立測試
- ✅ 更容易維護：修改影響範圍小
- ✅ 更容易理解：職責單一，代碼清晰

## 📚 參考文檔

- [CLAUDE.md - Linus 方法論](../../CLAUDE.md)
- [AI Agent 自動化文檔](../../docs/ai_agent/development_log.md)
- [進度更新器](../../docs/ai_agent/progress_report.md)

## 💡 擴展性示例

新增支援 `nose2` 框架（未來）：
```bash
# 1. 創建新文件
touch scripts/parsers/nose2_parser.py

# 2. 實作 BaseTestParser
class Nose2Parser(BaseTestParser):
    def can_parse(self, output: str) -> bool:
        return 'nose2' in output

# 3. 註冊到 Facade
# 在 __init__.py 中添加到 self.parsers 列表

# 完成！無需修改其他代碼
```

## 🏷️ 標籤

`refactoring` `technical-debt` `high-priority` `linus-methodology` `testing` `week-2`

## ⏱️ 預估工時

**3-4 天**

**分解：**
- Day 1: 創建基礎架構和抽象基類
- Day 2: 拆分各框架解析器
- Day 3: Facade 包裝 + 向後相容性測試
- Day 4: 整合測試 + 文檔更新
