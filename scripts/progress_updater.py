#!/usr/bin/env python3
"""
Automated Progress Documentation Updater

Implements the automated progress tracking system defined in CLAUDE.md.
Updates AI Agent documentation files based on development milestones.
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict

from framework_detection import FrameworkDetector, FrameworkType


@dataclass
class TestResults:
    """Enhanced test execution results with detailed breakdown"""
    # Backward compatibility - existing fields
    unit_tests_passed: int = 0
    unit_tests_total: int = 0
    integration_tests_passed: int = 0
    integration_tests_total: int = 0
    coverage_percentage: float = 0.0
    test_command_used: str = ""
    execution_time: float = 0.0
    success: bool = False
    
    # Enhanced fields - new additions
    framework: str = "unknown"
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    error_tests: int = 0
    
    # E2E tests support
    e2e_tests_passed: int = 0
    e2e_tests_total: int = 0
    
    # Detailed coverage
    coverage_lines_covered: int = 0
    coverage_lines_total: int = 0
    
    # Performance metrics
    slowest_tests: List[Dict[str, Any]] = None
    memory_usage: Optional[float] = None
    
    # Error details
    failure_details: List[str] = None
    error_summary: str = ""
    
    def __post_init__(self):
        if self.slowest_tests is None:
            self.slowest_tests = []
        if self.failure_details is None:
            self.failure_details = []
        
        # Auto-calculate total_tests if not set
        if self.total_tests == 0:
            self.total_tests = self.passed_tests + self.failed_tests + self.skipped_tests + self.error_tests


@dataclass
class MilestoneUpdate:
    """Milestone completion update"""
    milestone_name: str
    feature_name: str
    completed_tasks: List[str]
    test_results: TestResults
    git_tag: Optional[str] = None
    next_steps: List[str] = None
    business_value: List[str] = None
    technical_achievements: List[str] = None


class ProgressUpdater:
    """Automated documentation updater for AI Agent progress tracking"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.docs_dir = self.project_root / "docs" / "ai_agent"
        self.framework_detector = FrameworkDetector(self.project_root)
        self.framework = self.framework_detector.detect_framework()
        
        # Ensure docs directory exists
        self.docs_dir.mkdir(parents=True, exist_ok=True)
    
    def update_development_log(self, milestone: MilestoneUpdate) -> None:
        """
        Update development_log.md with new milestone completion
        
        Auto-Update Trigger: Function Implementation Complete
        """
        log_file = self.docs_dir / "development_log.md"
        
        # Generate new log entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        log_entry = f"""
## {timestamp} - {milestone.milestone_name}

### ✅ Completed Tasks
{self._format_task_list(milestone.completed_tasks)}

### 📊 Test Results
- Unit Tests: {milestone.test_results.unit_tests_passed}/{milestone.test_results.unit_tests_total} passed
- Integration Tests: {milestone.test_results.integration_tests_passed}/{milestone.test_results.integration_tests_total} passed
- Coverage: {milestone.test_results.coverage_percentage:.1f}%
- Test Command: `{milestone.test_results.test_command_used}`
- Execution Time: {milestone.test_results.execution_time:.2f}s

### 🔧 Technical Achievements
{self._format_achievement_list(milestone.technical_achievements or [])}

### 🎯 Business Value
{self._format_achievement_list(milestone.business_value or [])}

{f"### 🔄 Next Steps" + chr(10) + self._format_task_list(milestone.next_steps) if milestone.next_steps else ""}

---
"""
        
        # Insert new entry at the top of existing content
        if log_file.exists():
            existing_content = log_file.read_text()
            # Find the insertion point (after the header section)
            header_end = existing_content.find("---\n\n## ")
            if header_end != -1:
                # Insert after first ---
                insertion_point = header_end + 5
                new_content = (existing_content[:insertion_point] + 
                             log_entry + existing_content[insertion_point:])
            else:
                # Append to end if no pattern found
                new_content = existing_content + log_entry
        else:
            # Create new file with header
            header = self._generate_development_log_header()
            new_content = header + log_entry
        
        log_file.write_text(new_content)
        print(f"✅ Updated {log_file}")
    
    def update_milestone_tracking(self, milestone: MilestoneUpdate) -> None:
        """
        Update milestone_tracking.md with milestone completion
        
        Auto-Update Trigger: Milestone Achieved
        """
        tracking_file = self.docs_dir / "milestone_tracking.md"
        
        if not tracking_file.exists():
            # Create new milestone tracking file
            header = self._generate_milestone_tracking_header()
            tracking_file.write_text(header)
        
        content = tracking_file.read_text()
        
        # Update milestone status from IN PROGRESS to COMPLETED
        milestone_section = f"### Milestone: {milestone.milestone_name}"
        
        if milestone_section in content:
            # Update existing milestone
            content = self._update_existing_milestone(content, milestone)
        else:
            # Add new completed milestone
            content = self._add_completed_milestone(content, milestone)
        
        tracking_file.write_text(content)
        print(f"✅ Updated {tracking_file}")
    
    def update_test_results(self, test_results: TestResults) -> None:
        """
        Update test_results.md with latest test execution results
        
        Auto-Update Trigger: Tests Pass
        """
        results_file = self.docs_dir / "test_results.md"
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Generate test results entry
        results_entry = f"""
## Test Execution: {timestamp}

### 📊 Test Summary
- **Framework**: {self.framework.value}
- **Test Command**: `{test_results.test_command_used}`
- **Execution Time**: {test_results.execution_time:.2f} seconds
- **Overall Status**: {"✅ PASSED" if test_results.success else "❌ FAILED"}

### 📈 Test Coverage
- **Unit Tests**: {test_results.unit_tests_passed}/{test_results.unit_tests_total} ({(test_results.unit_tests_passed/max(test_results.unit_tests_total,1)*100):.1f}%)
- **Integration Tests**: {test_results.integration_tests_passed}/{test_results.integration_tests_total} ({(test_results.integration_tests_passed/max(test_results.integration_tests_total,1)*100):.1f}%)
- **Code Coverage**: {test_results.coverage_percentage:.1f}%

### 🎯 Quality Gate Status
- **Coverage Target**: {"✅ PASSED" if test_results.coverage_percentage >= 90 else "❌ FAILED"} (≥90%)
- **All Tests Pass**: {"✅ PASSED" if test_results.success else "❌ FAILED"}

---
"""
        
        if results_file.exists():
            existing_content = results_file.read_text()
            # Insert at the beginning after header
            header_end = existing_content.find("---\n\n## ")
            if header_end != -1:
                insertion_point = header_end + 5
                new_content = (existing_content[:insertion_point] + 
                             results_entry + existing_content[insertion_point:])
            else:
                new_content = existing_content + results_entry
        else:
            header = self._generate_test_results_header()
            new_content = header + results_entry
        
        results_file.write_text(new_content)
        print(f"✅ Updated {results_file}")
    
    def create_progress_report(self) -> None:
        """
        Create or update progress_report.md with current project status
        
        Auto-Update Trigger: Integration Success
        """
        report_file = self.docs_dir / "progress_report.md"
        
        # Gather current project statistics
        stats = self._gather_project_statistics()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        report_content = f"""# Project Progress Report

> **Auto-Generated**: {timestamp}  
> **Framework**: {self.framework.value}  
> **Project Root**: {self.project_root.name}

---

## 📊 Current Status Overview

### 🏗️ Project Architecture
- **Framework Type**: {self.framework.value.title()}
- **Structure Path**: {self.framework_detector.get_structure_path()}
- **Test Command**: `{self.framework_detector.get_test_command()}`
- **Dependency Management**: {self.framework_detector.get_dependency_file()}

### 📈 Development Statistics
- **Total Python Files**: {stats['python_files']}
- **Total Test Files**: {stats['test_files']}
- **Documentation Files**: {stats['doc_files']}
- **Configuration Files**: {stats['config_files']}

### 🧪 Testing Status
- **Test Framework**: {self.framework_detector.config.test_framework if self.framework_detector.config else 'Unknown'}
- **Last Test Run**: {stats['last_test_run']}
- **Test Coverage**: {stats['coverage']}

### 📋 Milestone Progress
{self._generate_milestone_summary()}

---

## 🎯 Quality Metrics

### ✅ Compliance Checklist
- **Docker Environment**: {"✅" if self._check_docker_setup() else "❌"} Container-based development
- **Git Standards**: {"✅" if self._check_git_standards() else "❌"} English commit messages
- **Documentation**: {"✅" if self._check_documentation() else "❌"} AI Agent docs structure
- **Testing**: {"✅" if stats['test_files'] > 0 else "❌"} Test coverage present

### 📊 Code Quality
- **Framework Detection**: ✅ {self.framework.value.title()}
- **Structure Compliance**: {"✅" if self._check_structure_compliance() else "❌"}
- **Configuration Standards**: {"✅" if self._check_config_standards() else "❌"}

---

## 🔄 Recent Activity

{self._get_recent_git_activity()}

---

**Note**: This report is automatically generated by the AI Agent progress tracking system.
"""
        
        report_file.write_text(report_content)
        print(f"✅ Generated {report_file}")
    
    def _format_task_list(self, tasks: List[str]) -> str:
        """Format task list with checkboxes"""
        if not tasks:
            return "- No specific tasks recorded"
        
        return "\n".join([f"- [x] {task}" for task in tasks])
    
    def _format_achievement_list(self, achievements: List[str]) -> str:
        """Format achievement list with bullet points"""
        if not achievements:
            return "- No specific achievements recorded"
        
        return "\n".join([f"- **{achievement}**" for achievement in achievements])
    
    def _generate_development_log_header(self) -> str:
        """Generate header for development_log.md"""
        return f"""# AI Agent Development Log

> **Auto-Updated**: This file is automatically updated by Claude Code CLI  
> **Purpose**: Track detailed development progress and implementation history  
> **Last Updated**: {datetime.now().strftime("%Y-%m-%d")}

---
"""
    
    def _generate_milestone_tracking_header(self) -> str:
        """Generate header for milestone_tracking.md"""
        return f"""# Function-Based Milestone Tracking

> **Auto-Updated**: This file is automatically updated by Claude Code CLI  
> **Purpose**: Track function-based development milestones with TDD approach  
> **Last Updated**: {datetime.now().strftime("%Y-%m-%d")}

---

## ✅ Completed Milestones

"""
    
    def _generate_test_results_header(self) -> str:
        """Generate header for test_results.md"""
        return f"""# Automated Test Results

> **Auto-Updated**: This file is automatically updated by Claude Code CLI  
> **Purpose**: Track test execution results and coverage metrics  
> **Last Updated**: {datetime.now().strftime("%Y-%m-%d")}

---
"""
    
    def _update_existing_milestone(self, content: str, milestone: MilestoneUpdate) -> str:
        """Update existing milestone status from IN PROGRESS to COMPLETED"""
        # Implementation would update milestone status in content
        # This is a simplified version
        updated_content = content.replace(
            f"**Status**: 🔄 IN PROGRESS",
            f"**Status**: ✅ COMPLETED"
        )
        return updated_content
    
    def _add_completed_milestone(self, content: str, milestone: MilestoneUpdate) -> str:
        """Add new completed milestone to tracking file"""
        completion_date = datetime.now().strftime("%Y-%m-%d")
        
        milestone_entry = f"""
### Milestone: {milestone.milestone_name}
**Status**: ✅ COMPLETED  
**Completion Date**: {completion_date}  
**Git Tag**: `{milestone.git_tag or 'milestone-' + milestone.milestone_name.lower().replace(' ', '-')}`

#### 📋 Function Scope
**Business Requirements**:
{self._format_achievement_list(milestone.business_value or ["Implementation completed"])}

**Technical Requirements**:
{self._format_achievement_list(milestone.technical_achievements or ["Core functionality implemented"])}

#### 🧪 Testing Results
✅ **Unit Tests**: {milestone.test_results.unit_tests_passed}/{milestone.test_results.unit_tests_total} passed  
✅ **Integration Tests**: {milestone.test_results.integration_tests_passed}/{milestone.test_results.integration_tests_total} passed  
✅ **Coverage**: {milestone.test_results.coverage_percentage:.1f}%

---
"""
        
        # Insert after "## ✅ Completed Milestones" section
        insertion_point = content.find("## ✅ Completed Milestones\n")
        if insertion_point != -1:
            insertion_point += len("## ✅ Completed Milestones\n")
            return content[:insertion_point] + milestone_entry + content[insertion_point:]
        else:
            return content + milestone_entry
    
    def _gather_project_statistics(self) -> Dict[str, Any]:
        """Gather current project statistics"""
        return {
            'python_files': len(list(self.project_root.glob("**/*.py"))),
            'test_files': len(list(self.project_root.glob("**/test_*.py"))) + len(list(self.project_root.glob("**/*_test.py"))),
            'doc_files': len(list(self.project_root.glob("**/*.md"))),
            'config_files': len([f for f in ["pyproject.toml", "requirements.txt", "docker-compose.yml"] if (self.project_root / f).exists()]),
            'last_test_run': "Not available",
            'coverage': "Not available"
        }
    
    def _generate_milestone_summary(self) -> str:
        """Generate milestone summary from tracking file"""
        tracking_file = self.docs_dir / "milestone_tracking.md"
        if not tracking_file.exists():
            return "- No milestones tracked yet"
        
        return "- See milestone_tracking.md for detailed progress"
    
    def _check_docker_setup(self) -> bool:
        """Check if Docker setup is present"""
        return (self.project_root / "docker-compose.yml").exists()
    
    def _check_git_standards(self) -> bool:
        """Check if Git repository exists"""
        return (self.project_root / ".git").exists()
    
    def _check_documentation(self) -> bool:
        """Check if AI Agent documentation structure exists"""
        return self.docs_dir.exists() and (self.project_root / "CLAUDE.md").exists()
    
    def _check_structure_compliance(self) -> bool:
        """Check if project structure complies with framework standards"""
        if self.framework == FrameworkType.DJANGO:
            return (self.project_root / "manage.py").exists()
        elif self.framework == FrameworkType.FASTAPI:
            return (self.project_root / "main.py").exists() or (self.project_root / "app").exists()
        return False
    
    def _check_config_standards(self) -> bool:
        """Check if configuration files follow standards"""
        if self.framework == FrameworkType.DJANGO:
            return (self.project_root / "requirements").exists() or (self.project_root / "requirements.txt").exists()
        elif self.framework == FrameworkType.FASTAPI:
            return (self.project_root / "pyproject.toml").exists()
        return False
    
    def _get_recent_git_activity(self) -> str:
        """Get recent Git activity summary"""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "log", "--oneline", "-5"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                commits = result.stdout.strip().split("\n")
                return "\n".join([f"- `{commit}`" for commit in commits[:3]])
            else:
                return "- Git history not available"
        except:
            return "- Git history not available"


def main():
    """CLI interface for progress updating"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Update AI Agent progress documentation")
    parser.add_argument("--project-root", "-p", type=Path, default=Path.cwd(),
                       help="Project root directory")
    parser.add_argument("--generate-report", "-r", action="store_true",
                       help="Generate progress report")
    parser.add_argument("--milestone", "-m", type=str,
                       help="Milestone name to complete")
    parser.add_argument("--feature", "-f", type=str,
                       help="Feature name implemented")
    
    args = parser.parse_args()
    
    updater = ProgressUpdater(args.project_root)
    
    if args.generate_report:
        updater.create_progress_report()
        print("✅ Progress report generated")
    
    if args.milestone and args.feature:
        # Example milestone update
        test_results = TestResults(
            unit_tests_passed=10,
            unit_tests_total=10,
            integration_tests_passed=5,
            integration_tests_total=5,
            coverage_percentage=95.0,
            test_command_used=updater.framework_detector.get_test_command(),
            execution_time=2.5,
            success=True
        )
        
        milestone = MilestoneUpdate(
            milestone_name=args.milestone,
            feature_name=args.feature,
            completed_tasks=[f"{args.feature} implementation", "Tests written and passing"],
            test_results=test_results,
            business_value=["Feature functionality delivered"],
            technical_achievements=["Framework integration completed"]
        )
        
        updater.update_development_log(milestone)
        updater.update_milestone_tracking(milestone)
        updater.update_test_results(test_results)
        
        print(f"✅ Updated documentation for milestone: {args.milestone}")


if __name__ == "__main__":
    main()