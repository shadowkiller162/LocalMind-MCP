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
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from progress_updater import TestResults


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
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
    
    def run_and_parse_tests(self, test_command: str) -> TestExecution:
        """
        Execute test command and parse results
        
        Args:
            test_command: Full test command to execute (e.g., "docker compose exec django pytest")
        """
        import time
        
        start_time = time.time()
        
        try:
            # Execute test command
            result = subprocess.run(
                test_command.split(),
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
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
            return TestExecution(
                command=test_command,
                output="Test execution timed out after 5 minutes",
                return_code=1,
                execution_time=execution_time,
                results=TestResults(
                    test_command_used=test_command,
                    execution_time=execution_time,
                    success=False
                )
            )
    
    def _parse_test_output(self, output: str, command: str) -> TestResults:
        """Parse test output based on framework type"""
        
        # Initialize results
        results = TestResults(test_command_used=command)
        
        # Detect test framework from command and output
        if "pytest" in command.lower() or "pytest" in output.lower():
            return self._parse_pytest_output(output, results)
        elif "python manage.py test" in command or "django" in output.lower():
            return self._parse_django_test_output(output, results)
        else:
            return self._parse_generic_output(output, results)
    
    def _parse_pytest_output(self, output: str, results: TestResults) -> TestResults:
        """Parse pytest output format"""
        
        # Parse test summary line (e.g., "10 passed, 2 failed, 1 skipped")
        summary_pattern = r"(\d+)\s+passed(?:,\s+(\d+)\s+failed)?(?:,\s+(\d+)\s+skipped)?"
        summary_match = re.search(summary_pattern, output, re.IGNORECASE)
        
        if summary_match:
            passed = int(summary_match.group(1))
            failed = int(summary_match.group(2) or 0)
            skipped = int(summary_match.group(3) or 0)
            
            # Assume all tests are unit tests unless specified otherwise
            results.unit_tests_passed = passed
            results.unit_tests_total = passed + failed
        
        # Parse coverage if present
        coverage_pattern = r"TOTAL\s+\d+\s+\d+\s+(\d+)%"
        coverage_match = re.search(coverage_pattern, output)
        if coverage_match:
            results.coverage_percentage = float(coverage_match.group(1))
        
        # Alternative coverage pattern
        alt_coverage_pattern = r"Total coverage:\s+(\d+\.?\d*)%"
        alt_coverage_match = re.search(alt_coverage_pattern, output)
        if alt_coverage_match:
            results.coverage_percentage = float(alt_coverage_match.group(1))
        
        # Parse execution time
        time_pattern = r"(\d+\.?\d*)\s*seconds?"
        # Look in last few lines of output
        last_lines = '\n'.join(output.split('\n')[-5:])
        time_match = re.search(time_pattern, last_lines)
        if time_match:
            results.execution_time = float(time_match.group(1))
        
        # Check for integration test indicators
        if "integration" in output.lower() or "e2e" in output.lower():
            # Try to separate integration tests (rough heuristic)
            integration_pattern = r"integration.*?(\d+)\s+passed"
            integration_match = re.search(integration_pattern, output, re.IGNORECASE)
            if integration_match:
                results.integration_tests_passed = int(integration_match.group(1))
                results.integration_tests_total = results.integration_tests_passed
                results.unit_tests_total -= results.integration_tests_passed
                results.unit_tests_passed -= results.integration_tests_passed
        
        return results
    
    def _parse_django_test_output(self, output: str, results: TestResults) -> TestResults:
        """Parse Django test runner output"""
        
        # Django test pattern: "Ran X tests in Y seconds"
        test_pattern = r"Ran (\d+) tests? in ([\d.]+)s"
        test_match = re.search(test_pattern, output)
        
        if test_match:
            total_tests = int(test_match.group(1))
            execution_time = float(test_match.group(2))
            results.execution_time = execution_time
            
            # Check for failures
            if "FAILED" in output or "ERROR" in output:
                failure_pattern = r"FAILED \((?:failures=(\d+))?(?:, ?errors=(\d+))?\)"
                failure_match = re.search(failure_pattern, output)
                if failure_match:
                    failures = int(failure_match.group(1) or 0)
                    errors = int(failure_match.group(2) or 0)
                    failed_total = failures + errors
                    
                    results.unit_tests_total = total_tests
                    results.unit_tests_passed = total_tests - failed_total
                else:
                    # Assume all failed if we can't parse specifics
                    results.unit_tests_total = total_tests
                    results.unit_tests_passed = 0
            else:
                # All tests passed
                results.unit_tests_total = total_tests
                results.unit_tests_passed = total_tests
        
        # Django doesn't typically include coverage, but check anyway
        coverage_match = re.search(r"(\d+)%\s+coverage", output)
        if coverage_match:
            results.coverage_percentage = float(coverage_match.group(1))
        
        return results
    
    def _parse_generic_output(self, output: str, results: TestResults) -> TestResults:
        """Parse generic test output when framework is unknown"""
        
        # Look for common success indicators
        success_indicators = [
            r"all tests? passed",
            r"(\d+) passed",
            r"tests?: (\d+) passed",
            r"success",
        ]
        
        for pattern in success_indicators:
            match = re.search(pattern, output, re.IGNORECASE)
            if match and len(match.groups()) > 0:
                try:
                    passed = int(match.group(1))
                    results.unit_tests_passed = passed
                    results.unit_tests_total = passed
                    break
                except (ValueError, IndexError):
                    continue
        
        # Look for failure indicators
        failure_pattern = r"(\d+)\s+failed"
        failure_match = re.search(failure_pattern, output, re.IGNORECASE)
        if failure_match:
            failed = int(failure_match.group(1))
            results.unit_tests_total += failed
        
        return results
    
    def generate_test_report(self, execution: TestExecution) -> Dict:
        """Generate structured test report"""
        return {
            "timestamp": TestExecution.__annotations__.get("timestamp", ""),
            "command": execution.command,
            "return_code": execution.return_code,
            "execution_time": execution.execution_time,
            "success": execution.results.success,
            "results": {
                "unit_tests": {
                    "passed": execution.results.unit_tests_passed,
                    "total": execution.results.unit_tests_total,
                    "success_rate": execution.results.unit_tests_passed / max(execution.results.unit_tests_total, 1) * 100
                },
                "integration_tests": {
                    "passed": execution.results.integration_tests_passed,
                    "total": execution.results.integration_tests_total,
                    "success_rate": execution.results.integration_tests_passed / max(execution.results.integration_tests_total, 1) * 100
                },
                "coverage": execution.results.coverage_percentage
            },
            "output_preview": execution.output[:500] + "..." if len(execution.output) > 500 else execution.output
        }


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