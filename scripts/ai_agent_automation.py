#!/usr/bin/env python3
"""
AI Agent Development Automation

Main automation script that implements the CLAUDE.md framework requirements.
Provides unified interface for all AI Agent automation functions.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import argparse

# Import our automation modules
from framework_detection import FrameworkDetector, FrameworkType
from progress_updater import ProgressUpdater, MilestoneUpdate, TestResults
from test_result_parser import TestResultParser


class AIAgentAutomation:
    """
    Main automation orchestrator for AI Agent development workflow
    
    Implements the automated triggers defined in CLAUDE.md:
    - Function Implementation Complete: Update development_log.md
    - Tests Pass: Update test_results.md  
    - Milestone Achieved: Update milestone_tracking.md
    - Integration Success: Update progress_report.md
    """
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.framework_detector = FrameworkDetector(self.project_root)
        self.progress_updater = ProgressUpdater(self.project_root)
        self.test_parser = TestResultParser(self.project_root)
        
        # Detect framework on initialization
        self.framework = self.framework_detector.detect_framework()
        
        print(f"🤖 AI Agent Automation initialized")
        print(f"📁 Project: {self.project_root.name}")
        print(f"🏗️  Framework: {self.framework.value}")
    
    def trigger_function_complete(self, function_name: str, tasks: List[str] = None, 
                                 business_value: List[str] = None, 
                                 technical_achievements: List[str] = None) -> bool:
        """
        Trigger: Function Implementation Complete
        Updates: development_log.md
        
        Args:
            function_name: Name of completed function/feature
            tasks: List of completed tasks
            business_value: Business value delivered
            technical_achievements: Technical accomplishments
        """
        print(f"🎯 Triggering Function Complete: {function_name}")
        
        try:
            # Run tests to get current status
            test_command = self.framework_detector.get_test_command()
            test_execution = self.test_parser.run_and_parse_tests(test_command)
            
            # Create milestone update
            milestone = MilestoneUpdate(
                milestone_name=f"Function: {function_name}",
                feature_name=function_name,
                completed_tasks=tasks or [f"{function_name} implementation completed"],
                test_results=test_execution.results,
                business_value=business_value or ["Feature functionality delivered"],
                technical_achievements=technical_achievements or ["Core implementation completed"]
            )
            
            # Update development log
            self.progress_updater.update_development_log(milestone)
            
            print(f"✅ Development log updated for {function_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update development log: {e}")
            return False
    
    def trigger_tests_pass(self, test_command: str = None) -> bool:
        """
        Trigger: Tests Pass
        Updates: test_results.md
        
        Args:
            test_command: Custom test command (optional)
        """
        print(f"🧪 Triggering Tests Pass")
        
        try:
            # Use provided command or detect from framework
            command = test_command or self.framework_detector.get_test_command()
            
            # Execute and parse tests
            test_execution = self.test_parser.run_and_parse_tests(command)
            
            # Update test results
            self.progress_updater.update_test_results(test_execution.results)
            
            status = "PASSED" if test_execution.results.success else "FAILED"
            print(f"✅ Test results updated - Status: {status}")
            return test_execution.results.success
            
        except Exception as e:
            print(f"❌ Failed to update test results: {e}")
            return False
    
    def trigger_milestone_achieved(self, milestone_name: str, git_tag: str = None,
                                  next_steps: List[str] = None) -> bool:
        """
        Trigger: Milestone Achieved
        Updates: milestone_tracking.md
        
        Args:
            milestone_name: Name of achieved milestone
            git_tag: Git tag for milestone (optional)
            next_steps: Next development steps
        """
        print(f"🏁 Triggering Milestone Achieved: {milestone_name}")
        
        try:
            # Run tests to validate milestone completion
            test_command = self.framework_detector.get_test_command()
            test_execution = self.test_parser.run_and_parse_tests(test_command)
            
            # Create Git tag if specified
            if git_tag:
                self._create_git_tag(git_tag, f"Milestone: {milestone_name}")
            
            # Create milestone update
            milestone = MilestoneUpdate(
                milestone_name=milestone_name,
                feature_name=milestone_name,
                completed_tasks=[f"{milestone_name} milestone completed"],
                test_results=test_execution.results,
                git_tag=git_tag,
                next_steps=next_steps or ["Continue to next milestone"],
                business_value=[f"{milestone_name} value delivered"],
                technical_achievements=[f"{milestone_name} implementation completed"]
            )
            
            # Update milestone tracking
            self.progress_updater.update_milestone_tracking(milestone)
            
            print(f"✅ Milestone tracking updated for {milestone_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update milestone tracking: {e}")
            return False
    
    def trigger_integration_success(self) -> bool:
        """
        Trigger: Integration Success
        Updates: progress_report.md
        """
        print(f"🔗 Triggering Integration Success")
        
        try:
            # Generate comprehensive progress report
            self.progress_updater.create_progress_report()
            
            print(f"✅ Progress report generated")
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate progress report: {e}")
            return False
    
    def run_full_automation_cycle(self, milestone_name: str, function_name: str = None) -> bool:
        """
        Run complete automation cycle for milestone completion
        
        Executes all triggers in sequence:
        1. Tests Pass -> update test_results.md
        2. Function Complete -> update development_log.md  
        3. Milestone Achieved -> update milestone_tracking.md
        4. Integration Success -> update progress_report.md
        """
        print(f"🚀 Running Full Automation Cycle: {milestone_name}")
        
        results = []
        
        # 1. Tests Pass
        print(f"\n📋 Step 1: Validating Tests")
        test_result = self.trigger_tests_pass()
        results.append(("Tests Pass", test_result))
        
        if not test_result:
            print(f"⚠️  Tests failed - continuing with documentation updates")
        
        # 2. Function Complete (if specified)
        if function_name:
            print(f"\n📋 Step 2: Recording Function Completion")
            function_result = self.trigger_function_complete(function_name)
            results.append(("Function Complete", function_result))
        
        # 3. Milestone Achieved
        print(f"\n📋 Step 3: Recording Milestone Achievement")
        git_tag = f"milestone-{milestone_name.lower().replace(' ', '-')}"
        milestone_result = self.trigger_milestone_achieved(milestone_name, git_tag)
        results.append(("Milestone Achieved", milestone_result))
        
        # 4. Integration Success
        print(f"\n📋 Step 4: Updating Progress Report")
        integration_result = self.trigger_integration_success()
        results.append(("Integration Success", integration_result))
        
        # Summary
        print(f"\n📊 Automation Cycle Results:")
        for step, success in results:
            status = "✅" if success else "❌"
            print(f"   {status} {step}")
        
        all_success = all(result for _, result in results)
        
        if all_success:
            print(f"\n🎉 Full automation cycle completed successfully!")
        else:
            print(f"\n⚠️  Some automation steps failed - check logs above")
        
        return all_success
    
    def validate_framework_compliance(self) -> Dict[str, bool]:
        """
        Validate project compliance with CLAUDE.md framework requirements
        """
        print(f"🔍 Validating Framework Compliance")
        
        compliance = {}
        
        # 1. Docker Environment
        docker_compose = (self.project_root / "docker-compose.yml").exists()
        compliance["docker_environment"] = docker_compose
        
        # 2. Documentation Structure
        claude_md = (self.project_root / "CLAUDE.md").exists()
        docs_structure = (self.project_root / "docs" / "ai_agent").exists()
        compliance["documentation_structure"] = claude_md and docs_structure
        
        # 3. Git Repository
        git_repo = (self.project_root / ".git").exists()
        compliance["git_repository"] = git_repo
        
        # 4. Framework Detection
        framework_detected = self.framework != FrameworkType.UNKNOWN
        compliance["framework_detection"] = framework_detected
        
        # 5. Test Structure
        test_files = len(list(self.project_root.glob("**/test_*.py"))) + len(list(self.project_root.glob("**/*_test.py")))
        compliance["test_structure"] = test_files > 0
        
        # 6. Configuration Files
        if self.framework == FrameworkType.DJANGO:
            config_compliance = (self.project_root / "requirements").exists() or (self.project_root / "requirements.txt").exists()
        elif self.framework == FrameworkType.FASTAPI:
            config_compliance = (self.project_root / "pyproject.toml").exists()
        else:
            config_compliance = False
        compliance["configuration_files"] = config_compliance
        
        # Print compliance report
        print(f"\n📊 Compliance Report:")
        for check, passed in compliance.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check.replace('_', ' ').title()}")
        
        overall_compliance = all(compliance.values())
        print(f"\n🎯 Overall Compliance: {'✅ PASSED' if overall_compliance else '❌ FAILED'}")
        
        return compliance
    
    def _create_git_tag(self, tag_name: str, message: str) -> bool:
        """Create Git tag for milestone"""
        try:
            subprocess.run(
                ["git", "tag", "-a", tag_name, "-m", message],
                cwd=self.project_root,
                check=True,
                capture_output=True
            )
            print(f"🏷️  Created Git tag: {tag_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Failed to create Git tag: {e}")
            return False
    
    def get_framework_info(self) -> Dict:
        """Get detailed framework information"""
        return self.framework_detector.generate_detection_report()


def main():
    """CLI interface for AI Agent automation"""
    parser = argparse.ArgumentParser(
        description="AI Agent Development Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full automation cycle for milestone
  python ai_agent_automation.py --milestone "User Authentication" --full-cycle
  
  # Trigger function completion
  python ai_agent_automation.py --function-complete "login_api" 
  
  # Run tests and update docs
  python ai_agent_automation.py --tests-pass
  
  # Validate framework compliance
  python ai_agent_automation.py --validate
        """
    )
    
    parser.add_argument("--project-root", "-p", type=Path, default=Path.cwd(),
                       help="Project root directory")
    
    # Trigger actions
    parser.add_argument("--function-complete", "-f", type=str,
                       help="Mark function as complete and update docs")
    parser.add_argument("--tests-pass", "-t", action="store_true",
                       help="Record test pass and update test results")
    parser.add_argument("--milestone", "-m", type=str,
                       help="Mark milestone as achieved")
    parser.add_argument("--integration-success", "-i", action="store_true",
                       help="Generate integration success report")
    
    # Full automation
    parser.add_argument("--full-cycle", action="store_true",
                       help="Run complete automation cycle")
    
    # Validation and info
    parser.add_argument("--validate", "-v", action="store_true",
                       help="Validate framework compliance")
    parser.add_argument("--framework-info", action="store_true",
                       help="Show framework detection information")
    
    # Output format
    parser.add_argument("--json", "-j", action="store_true",
                       help="Output in JSON format")
    
    args = parser.parse_args()
    
    # Initialize automation
    automation = AIAgentAutomation(args.project_root)
    
    results = {}
    
    # Execute requested actions
    if args.validate:
        results["compliance"] = automation.validate_framework_compliance()
    
    if args.framework_info:
        results["framework"] = automation.get_framework_info()
    
    if args.tests_pass:
        results["tests_pass"] = automation.trigger_tests_pass()
    
    if args.function_complete:
        results["function_complete"] = automation.trigger_function_complete(args.function_complete)
    
    if args.milestone:
        if args.full_cycle:
            results["full_cycle"] = automation.run_full_automation_cycle(args.milestone, args.function_complete)
        else:
            results["milestone"] = automation.trigger_milestone_achieved(args.milestone)
    
    if args.integration_success:
        results["integration_success"] = automation.trigger_integration_success()
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2, default=str))
    
    # Determine exit code
    if results:
        # Exit with error if any automation failed
        failed_operations = [k for k, v in results.items() if isinstance(v, bool) and not v]
        if failed_operations:
            print(f"\n❌ Failed operations: {', '.join(failed_operations)}")
            sys.exit(1)
        else:
            print(f"\n✅ All operations completed successfully")
            sys.exit(0)
    else:
        print("No operations specified. Use --help for usage information.")
        sys.exit(0)


if __name__ == "__main__":
    main()