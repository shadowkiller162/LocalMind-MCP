#!/usr/bin/env python3
"""
Test Result Parser

Parses test output from pytest and Django test runners to extract structured results.
Supports coverage reporting integration for automated documentation updates.
"""

import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from progress_updater import TestResults


class TestFramework(Enum):
    """Supported test frameworks"""
    PYTEST = "pytest"
    DJANGO_TEST = "django_test"
    UNITTEST = "unittest"
    UNKNOWN = "unknown"


@dataclass
class TestExecution:
    """Test execution context and results"""
    command: str
    output: str
    return_code: int
    execution_time: float
    results: TestResults


class TestResultParser:
    """Parser for different test framework outputs"""
    
    # Enhanced test patterns for better parsing
    PYTEST_PATTERNS = {
        'summary': [
            r'=+ (\d+) failed,? (\d+) passed.*in ([\d.]+)s =+',
            r'=+ (\d+) passed.*in ([\d.]+)s =+',
            r'(\d+) passed(?:, (\d+) failed)?(?:, (\d+) skipped)?(?:, (\d+) error)?.*in ([\d.]+)s',
        ],
        'coverage': [
            r'TOTAL\s+(\d+)\s+(\d+)\s+(\d+)%',
            r'Total coverage: ([\d.]+)%',
            r'Coverage: ([\d.]+)%'
        ],
        'slow_tests': [
            r'([\d.]+)s call.*::(test_\w+)',
            r'(test_\w+).*?([\d.]+)s'
        ]
    }
    
    DJANGO_PATTERNS = {
        'summary': [
            r'Ran (\d+) tests? in ([\d.]+)s',
            r'FAILED \(failures=(\d+)(?:, errors=(\d+))?\)',
            r'OK'
        ],
        'failures': [
            r'FAIL: (test_\w+)',
            r'ERROR: (test_\w+)'
        ]
    }
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self._is_running_in_container = self._detect_container_environment()
        self.framework_detection_cache = {}
    
    def run_and_parse_tests(self, test_command: str) -> TestExecution:
        """
        Execute test command and parse results
        
        Args:
            test_command: Full test command to execute (e.g., "docker compose exec django pytest")
        """
        import time
        
        start_time = time.time()
        
        try:
            # Parse command to handle Docker container execution properly
            parsed_command = self._parse_command_for_container(test_command)
            
            # Execute test command
            result = subprocess.run(
                parsed_command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                shell=True  # Use shell for complex commands
            )
            
            execution_time = time.time() - start_time
            
            # Parse results based on output
            test_results = self._parse_test_output(result.stdout + result.stderr, test_command)
            test_results.execution_time = execution_time
            test_results.success = result.returncode == 0
            
            return TestExecution(
                command=test_command,
                output=result.stdout + result.stderr,
                return_code=result.returncode,
                execution_time=execution_time,
                results=test_results
            )
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            error_msg = f"Test execution timed out after 5 minutes. Command: {test_command}"
            return TestExecution(
                command=test_command,
                output=error_msg,
                return_code=1,
                execution_time=execution_time,
                results=TestResults(
                    test_command_used=test_command,
                    execution_time=execution_time,
                    success=False
                )
            )
        except FileNotFoundError as e:
            execution_time = time.time() - start_time
            error_msg = f"Command not found: {e}. Command: {test_command}\nTip: Make sure you're running this from the correct environment."
            return TestExecution(
                command=test_command,
                output=error_msg,
                return_code=127,
                execution_time=execution_time,
                results=TestResults(
                    test_command_used=test_command,
                    execution_time=execution_time,
                    success=False
                )
            )
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Unexpected error during test execution: {e}. Command: {test_command}"
            return TestExecution(
                command=test_command,
                output=error_msg,
                return_code=1,
                execution_time=execution_time,
                results=TestResults(
                    test_command_used=test_command,
                    execution_time=execution_time,
                    success=False
                )
            )
    
    def _detect_container_environment(self) -> bool:
        """Detect if we're running inside a Docker container"""
        try:
            # Check for /.dockerenv file (Docker creates this)
            if Path('/.dockerenv').exists():
                return True
            
            # Check for container indicators in /proc/1/cgroup
            if Path('/proc/1/cgroup').exists():
                with open('/proc/1/cgroup', 'r') as f:
                    content = f.read()
                    if 'docker' in content or 'containerd' in content:
                        return True
            
            return False
        except Exception:
            return False
    
    def _parse_command_for_container(self, test_command: str) -> str:
        """Parse command to work properly in container environment"""
        
        # If we're running inside a container and the command starts with "docker compose exec"
        if self._is_running_in_container and test_command.startswith("docker compose exec"):
            # Extract the actual command from "docker compose exec [service] [command]"
            parts = test_command.split()
            if len(parts) >= 4:  # docker compose exec service command...
                # Return just the command part (skip "docker compose exec service")
                return " ".join(parts[4:])  # Skip docker, compose, exec, service
            else:
                # Fallback to the original command if parsing fails
                return test_command
        
        # If we're not in a container, return the command as-is
        return test_command
    
    def detect_test_framework(self, command: str, output: str) -> TestFramework:
        """Detect test framework from command and output with caching"""
        
        # Check cache first
        cache_key = f"{command}_{hash(output[:200])}"
        if cache_key in self.framework_detection_cache:
            return self.framework_detection_cache[cache_key]
        
        framework = TestFramework.UNKNOWN
        
        # Command-based detection (most reliable)
        if 'pytest' in command.lower():
            framework = TestFramework.PYTEST
        elif 'manage.py test' in command.lower():
            framework = TestFramework.DJANGO_TEST
        elif 'python -m unittest' in command.lower():
            framework = TestFramework.UNITTEST
        
        # Output-based detection (fallback)
        if framework == TestFramework.UNKNOWN:
            if any(pattern in output.lower() for pattern in ['pytest', 'conftest', 'test session starts']):
                framework = TestFramework.PYTEST
            elif any(pattern in output.lower() for pattern in ['django', 'creating test database']):
                framework = TestFramework.DJANGO_TEST
            elif 'unittest' in output.lower():
                framework = TestFramework.UNITTEST
        
        # Cache result
        self.framework_detection_cache[cache_key] = framework
        return framework
    
    def _parse_test_output(self, output: str, command: str) -> TestResults:
        """Parse test output based on framework type"""
        
        # Initialize results
        results = TestResults(test_command_used=command)
        
        # Detect framework using enhanced detection
        framework = self.detect_test_framework(command, output)
        results.framework = framework.value
        
        # Parse based on detected framework
        if framework == TestFramework.PYTEST:
            self._parse_pytest_output_enhanced(output, results)
        elif framework == TestFramework.DJANGO_TEST:
            self._parse_django_test_output_enhanced(output, results)
        elif framework == TestFramework.UNITTEST:
            self._parse_unittest_output(output, results)
        else:
            self._parse_generic_output_enhanced(output, results)
        
        # Extract additional performance metrics and failure details
        self._extract_performance_metrics(output, results)
        if not results.success:
            self._extract_failure_details(output, results)
        
        return results
    
    def _parse_pytest_output_enhanced(self, output: str, results: TestResults) -> None:
        """Enhanced pytest output parsing with better pattern recognition"""
        
        # Parse main summary line with multiple patterns
        for pattern in self.PYTEST_PATTERNS['summary']:
            match = re.search(pattern, output, re.IGNORECASE | re.MULTILINE)
            if match:
                self._extract_pytest_counts(match, results)
                break
        
        # Parse coverage with multiple patterns
        for pattern in self.PYTEST_PATTERNS['coverage']:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                try:
                    if len(match.groups()) >= 3:  # TOTAL format
                        results.coverage_lines_covered = int(match.group(2))
                        results.coverage_lines_total = int(match.group(1)) + int(match.group(2))
                        results.coverage_percentage = float(match.group(3))
                    else:  # Percentage only format
                        results.coverage_percentage = float(match.group(1))
                except (ValueError, IndexError):
                    pass
                break
        
        # Parse test categories (unit vs integration vs e2e)
        self._categorize_tests_from_output(output, results)
        
        # Extract slow tests
        self._extract_slow_tests_pytest(output, results)
    
    def _parse_django_test_output_enhanced(self, output: str, results: TestResults) -> None:
        """Enhanced Django test output parsing"""
        
        # Parse "Ran X tests in Y seconds"
        ran_match = re.search(r'Ran (\d+) tests? in ([\d.]+)s', output)
        if ran_match:
            results.total_tests = int(ran_match.group(1))
            results.execution_time = float(ran_match.group(2))
        
        # Check for failures and errors
        if 'FAILED' in output:
            failure_match = re.search(r'FAILED \((?:failures=(\d+))?(?:, ?errors=(\d+))?\)', output)
            if failure_match:
                failures = int(failure_match.group(1) or 0)
                errors = int(failure_match.group(2) or 0)
                results.failed_tests = failures
                results.error_tests = errors
                results.passed_tests = results.total_tests - failures - errors
            else:
                # Assume all tests failed if we can't parse specifics
                results.failed_tests = results.total_tests
                results.passed_tests = 0
        elif 'OK' in output:
            results.passed_tests = results.total_tests
            results.failed_tests = 0
        
        # Django tests are typically unit tests unless otherwise specified
        results.unit_tests_total = results.total_tests
        results.unit_tests_passed = results.passed_tests
        
        # Check for coverage
        coverage_match = re.search(r"(\d+)%\s+coverage", output)
        if coverage_match:
            results.coverage_percentage = float(coverage_match.group(1))
    
    def _parse_unittest_output(self, output: str, results: TestResults) -> None:
        """Parse unittest output"""
        
        # Parse "Ran X tests in Y seconds"
        ran_match = re.search(r'Ran (\d+) tests? in ([\d.]+)s', output)
        if ran_match:
            results.total_tests = int(ran_match.group(1))
            results.execution_time = float(ran_match.group(2))
        
        # Check for OK or FAILED
        if 'OK' in output:
            results.passed_tests = results.total_tests
        elif 'FAILED' in output:
            # Try to extract failure count
            fail_match = re.search(r'failures=(\d+)', output)
            if fail_match:
                results.failed_tests = int(fail_match.group(1))
                results.passed_tests = results.total_tests - results.failed_tests
        
        results.unit_tests_total = results.total_tests
        results.unit_tests_passed = results.passed_tests
    
    def _parse_generic_output_enhanced(self, output: str, results: TestResults) -> None:
        """Enhanced generic output parsing with better heuristics"""
        
        # Look for common test result patterns
        patterns = [
            r'(\d+) tests?, (\d+) passed, (\d+) failed',
            r'(\d+) passed.*?(\d+) failed',
            r'Tests run: (\d+).*?Failures: (\d+)',
            r'(\d+) tests passed',
            r'(\d+) tests failed'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) >= 3:  # Full pattern
                    results.total_tests = int(groups[0])
                    results.passed_tests = int(groups[1])
                    results.failed_tests = int(groups[2])
                elif len(groups) == 2:  # Passed/failed only
                    results.passed_tests = int(groups[0])
                    results.failed_tests = int(groups[1])
                    results.total_tests = results.passed_tests + results.failed_tests
                elif 'passed' in pattern:
                    results.passed_tests = int(groups[0])
                    results.total_tests = results.passed_tests
                elif 'failed' in pattern:
                    results.failed_tests = int(groups[0])
                break
        
        results.unit_tests_total = results.total_tests
        results.unit_tests_passed = results.passed_tests
    
    def _extract_pytest_counts(self, match, results: TestResults) -> None:
        """Extract counts from pytest summary match"""
        groups = match.groups()
        
        # Handle different summary formats
        if 'failed' in match.group(0).lower() and 'passed' in match.group(0).lower():
            # Format: "X failed, Y passed in Z seconds"
            try:
                results.failed_tests = int(groups[0])
                results.passed_tests = int(groups[1])
                results.total_tests = results.failed_tests + results.passed_tests
                if len(groups) > 2:
                    results.execution_time = float(groups[2])
            except (ValueError, IndexError):
                pass
        elif 'passed' in match.group(0).lower():
            # Format: "X passed in Y seconds"
            try:
                results.passed_tests = int(groups[0])
                results.total_tests = results.passed_tests
                if len(groups) > 1:
                    results.execution_time = float(groups[1])
            except (ValueError, IndexError):
                pass
    
    def _categorize_tests_from_output(self, output: str, results: TestResults) -> None:
        """Categorize tests based on naming patterns and directory structure"""
        
        # Look for test categories in output
        unit_patterns = [r'test_unit', r'unit_test', r'tests/unit', r'unit/']
        integration_patterns = [r'test_integration', r'integration_test', r'tests/integration', r'integration/']
        e2e_patterns = [r'test_e2e', r'e2e_test', r'tests/e2e', r'e2e/', r'test_end_to_end']
        
        # Count occurrences of each pattern
        unit_count = sum(len(re.findall(pattern, output, re.IGNORECASE)) for pattern in unit_patterns)
        integration_count = sum(len(re.findall(pattern, output, re.IGNORECASE)) for pattern in integration_patterns)
        e2e_count = sum(len(re.findall(pattern, output, re.IGNORECASE)) for pattern in e2e_patterns)
        
        # Distribute tests based on patterns found
        if unit_count > 0 or integration_count > 0 or e2e_count > 0:
            total_categorized = unit_count + integration_count + e2e_count
            
            if total_categorized <= results.total_tests:
                results.unit_tests_total = unit_count
                results.integration_tests_total = integration_count
                results.e2e_tests_total = e2e_count
                
                # Assume passed tests are distributed proportionally
                if results.total_tests > 0:
                    pass_ratio = results.passed_tests / results.total_tests
                    results.unit_tests_passed = int(results.unit_tests_total * pass_ratio)
                    results.integration_tests_passed = int(results.integration_tests_total * pass_ratio)
                    results.e2e_tests_passed = int(results.e2e_tests_total * pass_ratio)
        else:
            # Default: assume all tests are unit tests
            results.unit_tests_total = results.total_tests
            results.unit_tests_passed = results.passed_tests
    
    def _extract_slow_tests_pytest(self, output: str, results: TestResults) -> None:
        """Extract slow test information from pytest output"""
        
        # Look for slowest tests section
        slowest_section = re.search(r'slowest.*?tests.*?\n(.*?)(?:\n=|$)', output, re.IGNORECASE | re.DOTALL)
        if slowest_section:
            slow_tests = []
            for line in slowest_section.group(1).split('\n'):
                time_match = re.search(r'([\d.]+)s.*?::(test_\w+)', line)
                if time_match:
                    slow_tests.append({
                        'test_name': time_match.group(2),
                        'duration': float(time_match.group(1))
                    })
            results.slowest_tests = slow_tests[:5]  # Keep top 5
    
    def _extract_performance_metrics(self, output: str, results: TestResults) -> None:
        """Extract additional performance metrics from output"""
        
        # Memory usage (if available)
        memory_match = re.search(r'memory usage:?\s*([\d.]+)\s*MB', output, re.IGNORECASE)
        if memory_match:
            results.memory_usage = float(memory_match.group(1))
    
    def _extract_failure_details(self, output: str, results: TestResults) -> None:
        """Extract failure details for debugging"""
        
        # Look for FAILURES section
        failures_section = re.search(r'FAILURES.*?\n(.*?)(?:\n=+|$)', output, re.DOTALL)
        if failures_section:
            failure_text = failures_section.group(1)
            
            # Extract individual test failures
            test_failures = re.findall(r'FAILED (test_\w+).*?\n(.*?)(?=FAILED|$)', failure_text, re.DOTALL)
            for test_name, error_detail in test_failures[:5]:  # Limit to 5 failures
                results.failure_details.append(f"{test_name}: {error_detail.strip()[:200]}...")
        
        # Set error summary
        if results.failed_tests > 0:
            results.error_summary = f"{results.failed_tests} test(s) failed"
        if results.error_tests > 0:
            results.error_summary += f", {results.error_tests} error(s)"
    
    def generate_test_report(self, execution: TestExecution) -> Dict:
        """Generate enhanced structured test report"""
        from datetime import datetime
        
        report = {
            "meta": {
                "timestamp": datetime.now().isoformat(),
                "framework": execution.results.framework,
                "command": execution.command,
                "execution_time": execution.execution_time,
                "success": execution.results.success,
                "return_code": execution.return_code
            },
            "summary": {
                "total_tests": execution.results.total_tests,
                "passed": execution.results.passed_tests,
                "failed": execution.results.failed_tests,
                "skipped": execution.results.skipped_tests,
                "errors": execution.results.error_tests,
                "success_rate": (execution.results.passed_tests / max(execution.results.total_tests, 1)) * 100 if execution.results.total_tests > 0 else 0.0
            },
            "categories": {
                "unit_tests": {
                    "total": execution.results.unit_tests_total,
                    "passed": execution.results.unit_tests_passed,
                    "success_rate": (execution.results.unit_tests_passed / max(execution.results.unit_tests_total, 1)) * 100 if execution.results.unit_tests_total > 0 else 0.0
                },
                "integration_tests": {
                    "total": execution.results.integration_tests_total,
                    "passed": execution.results.integration_tests_passed,
                    "success_rate": (execution.results.integration_tests_passed / max(execution.results.integration_tests_total, 1)) * 100 if execution.results.integration_tests_total > 0 else 0.0
                },
                "e2e_tests": {
                    "total": execution.results.e2e_tests_total,
                    "passed": execution.results.e2e_tests_passed,
                    "success_rate": (execution.results.e2e_tests_passed / max(execution.results.e2e_tests_total, 1)) * 100 if execution.results.e2e_tests_total > 0 else 0.0
                }
            },
            "coverage": {
                "percentage": execution.results.coverage_percentage,
                "lines_covered": execution.results.coverage_lines_covered,
                "lines_total": execution.results.coverage_lines_total
            },
            "performance": {
                "execution_time": execution.execution_time,
                "memory_usage": execution.results.memory_usage,
                "slowest_tests": execution.results.slowest_tests
            },
            "output_preview": execution.output[:500] + "..." if len(execution.output) > 500 else execution.output
        }
        
        if not execution.results.success:
            report["errors"] = {
                "summary": execution.results.error_summary,
                "failure_details": execution.results.failure_details[:3]  # Limit output
            }
        
        return report
    
    def generate_comprehensive_report(self, execution: TestExecution) -> Dict:
        """Generate comprehensive test report with all details (alias for backward compatibility)"""
        return self.generate_test_report(execution)


class CoverageReportParser:
    """Parser for coverage.py XML and JSON reports"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
    
    def parse_coverage_xml(self, xml_path: Path = None) -> Dict:
        """Parse coverage.xml file"""
        if xml_path is None:
            xml_path = self.project_root / "coverage.xml"
        
        if not xml_path.exists():
            return {"coverage": 0.0, "files": []}
        
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Parse overall coverage
            coverage_attr = root.get("line-rate")
            if coverage_attr:
                overall_coverage = float(coverage_attr) * 100
            else:
                overall_coverage = 0.0
            
            # Parse file-level coverage
            files = []
            for package in root.findall(".//package"):
                for cls in package.findall("classes/class"):
                    filename = cls.get("filename")
                    line_rate = float(cls.get("line-rate", 0))
                    files.append({
                        "filename": filename,
                        "coverage": line_rate * 100
                    })
            
            return {
                "coverage": overall_coverage,
                "files": files
            }
        
        except Exception as e:
            return {"coverage": 0.0, "files": [], "error": str(e)}
    
    def parse_coverage_json(self, json_path: Path = None) -> Dict:
        """Parse coverage.json file"""
        if json_path is None:
            json_path = self.project_root / "coverage.json"
        
        if not json_path.exists():
            return {"coverage": 0.0, "files": []}
        
        try:
            with open(json_path) as f:
                data = json.load(f)
            
            # Extract overall coverage
            totals = data.get("totals", {})
            percent_covered = totals.get("percent_covered", 0.0)
            
            # Extract file-level data
            files = []
            for filename, file_data in data.get("files", {}).items():
                summary = file_data.get("summary", {})
                coverage = summary.get("percent_covered", 0.0)
                files.append({
                    "filename": filename,
                    "coverage": coverage
                })
            
            return {
                "coverage": percent_covered,
                "files": files
            }
        
        except Exception as e:
            return {"coverage": 0.0, "files": [], "error": str(e)}


def main():
    """CLI interface for test result parsing"""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Parse test results and generate reports")
    parser.add_argument("--command", "-c", type=str, required=True,
                       help="Test command to execute")
    parser.add_argument("--project-root", "-p", type=Path, default=Path.cwd(),
                       help="Project root directory")
    parser.add_argument("--json", "-j", action="store_true",
                       help="Output results in JSON format")
    parser.add_argument("--update-docs", "-u", action="store_true",
                       help="Update AI Agent documentation with results")
    
    args = parser.parse_args()
    
    # Parse test results
    parser_instance = TestResultParser(args.project_root)
    execution = parser_instance.run_and_parse_tests(args.command)
    
    if args.json:
        report = parser_instance.generate_test_report(execution)
        print(json.dumps(report, indent=2))
    else:
        print(f"Test Execution Results:")
        print(f"Command: {execution.command}")
        print(f"Return Code: {execution.return_code}")
        print(f"Execution Time: {execution.execution_time:.2f}s")
        print(f"Success: {execution.results.success}")
        print(f"Unit Tests: {execution.results.unit_tests_passed}/{execution.results.unit_tests_total}")
        print(f"Coverage: {execution.results.coverage_percentage:.1f}%")
    
    if args.update_docs:
        from progress_updater import ProgressUpdater
        updater = ProgressUpdater(args.project_root)
        updater.update_test_results(execution.results)
        print("✅ Documentation updated")
    
    # Exit with test result code
    sys.exit(execution.return_code)


if __name__ == "__main__":
    main()