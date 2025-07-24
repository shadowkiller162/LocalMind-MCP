#!/usr/bin/env python3
"""
Framework Detection and Adaptation System

Automatically detects Django vs FastAPI projects and adapts AI Agent behavior accordingly.
Implements the framework detection logic defined in CLAUDE.md.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass


class FrameworkType(Enum):
    """Supported framework types"""
    DJANGO = "django"
    FASTAPI = "fastapi"
    UNKNOWN = "unknown"


@dataclass
class FrameworkConfig:
    """Framework-specific configuration"""
    framework: FrameworkType
    structure_path: str
    test_command: str
    test_framework: str
    dependency_file: str
    main_module: str
    app_detection_files: List[str]


class FrameworkDetector:
    """Detects and configures framework-specific settings"""
    
    FRAMEWORK_CONFIGS = {
        FrameworkType.DJANGO: FrameworkConfig(
            framework=FrameworkType.DJANGO,
            structure_path="apps/",
            test_command="docker compose exec django pytest",
            test_framework="pytest-django",
            dependency_file="requirements/base.txt",
            main_module="manage.py",
            app_detection_files=["manage.py", "wsgi.py", "asgi.py"]
        ),
        FrameworkType.FASTAPI: FrameworkConfig(
            framework=FrameworkType.FASTAPI,
            structure_path="app/",
            test_command="docker compose exec app pytest",
            test_framework="pytest",
            dependency_file="pyproject.toml",
            main_module="main.py",
            app_detection_files=["main.py", "app.py"]
        )
    }
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.framework_type = FrameworkType.UNKNOWN
        self.config: Optional[FrameworkConfig] = None
    
    def detect_framework(self) -> FrameworkType:
        """
        Detect framework type based on project structure and files
        
        Detection logic from CLAUDE.md:
        - Django: manage.py exists
        - FastAPI: main.py exists or 'fastapi' in requirements
        """
        # Check for Django indicators
        if self._check_django_indicators():
            self.framework_type = FrameworkType.DJANGO
            self.config = self.FRAMEWORK_CONFIGS[FrameworkType.DJANGO]
            return FrameworkType.DJANGO
        
        # Check for FastAPI indicators
        if self._check_fastapi_indicators():
            self.framework_type = FrameworkType.FASTAPI
            self.config = self.FRAMEWORK_CONFIGS[FrameworkType.FASTAPI]
            return FrameworkType.FASTAPI
        
        # Unknown framework
        self.framework_type = FrameworkType.UNKNOWN
        return FrameworkType.UNKNOWN
    
    def _check_django_indicators(self) -> bool:
        """Check for Django-specific files and patterns"""
        # Primary indicator: manage.py
        if (self.project_root / "manage.py").exists():
            return True
        
        # Secondary indicators
        django_indicators = [
            "wsgi.py",
            "asgi.py",
            "settings.py",
            "urls.py"
        ]
        
        for indicator in django_indicators:
            if list(self.project_root.glob(f"**/{indicator}")):
                return True
        
        # Check for Django in requirements
        if self._check_dependency("django"):
            return True
        
        return False
    
    def _check_fastapi_indicators(self) -> bool:
        """Check for FastAPI-specific files and patterns"""
        # Primary indicator: main.py with FastAPI
        main_py = self.project_root / "main.py"
        if main_py.exists():
            try:
                content = main_py.read_text()
                if "fastapi" in content.lower() or "FastAPI" in content:
                    return True
            except:
                pass
        
        # Check app.py
        app_py = self.project_root / "app.py"
        if app_py.exists():
            try:
                content = app_py.read_text()
                if "fastapi" in content.lower() or "FastAPI" in content:
                    return True
            except:
                pass
        
        # Check for FastAPI in dependencies
        if self._check_dependency("fastapi"):
            return True
        
        return False
    
    def _check_dependency(self, package_name: str) -> bool:
        """Check if package exists in project dependencies"""
        # Check requirements.txt files
        requirements_files = [
            "requirements.txt",
            "requirements/base.txt",
            "requirements/local.txt"
        ]
        
        for req_file in requirements_files:
            req_path = self.project_root / req_file
            if req_path.exists():
                try:
                    content = req_path.read_text().lower()
                    if package_name.lower() in content:
                        return True
                except:
                    pass
        
        # Check pyproject.toml
        pyproject = self.project_root / "pyproject.toml"
        if pyproject.exists():
            try:
                content = pyproject.read_text().lower()
                if package_name.lower() in content:
                    return True
            except:
                pass
        
        return False
    
    def get_test_command(self) -> str:
        """Get framework-appropriate test command"""
        if not self.config:
            self.detect_framework()
        
        return self.config.test_command if self.config else "pytest"
    
    def get_structure_path(self) -> str:
        """Get framework-appropriate app structure path"""
        if not self.config:
            self.detect_framework()
        
        return self.config.structure_path if self.config else ""
    
    def get_dependency_file(self) -> str:
        """Get framework-appropriate dependency file"""
        if not self.config:
            self.detect_framework()
        
        return self.config.dependency_file if self.config else "requirements.txt"
    
    def generate_detection_report(self) -> Dict:
        """Generate detailed detection report"""
        framework = self.detect_framework()
        
        report = {
            "framework": framework.value,
            "confidence": self._calculate_confidence(),
            "detection_indicators": self._get_detection_indicators(),
            "recommended_structure": self.get_structure_path(),
            "test_command": self.get_test_command(),
            "dependency_file": self.get_dependency_file(),
        }
        
        if self.config:
            report["config"] = {
                "test_framework": self.config.test_framework,
                "main_module": self.config.main_module,
                "app_detection_files": self.config.app_detection_files
            }
        
        return report
    
    def _calculate_confidence(self) -> float:
        """Calculate detection confidence score"""
        if self.framework_type == FrameworkType.UNKNOWN:
            return 0.0
        
        indicators = self._get_detection_indicators()
        total_possible = 5  # Max indicators we check
        found_indicators = len([i for i in indicators.values() if i])
        
        return found_indicators / total_possible
    
    def _get_detection_indicators(self) -> Dict[str, bool]:
        """Get detailed breakdown of detection indicators"""
        return {
            "manage_py_exists": (self.project_root / "manage.py").exists(),
            "main_py_exists": (self.project_root / "main.py").exists(),
            "django_in_deps": self._check_dependency("django"),
            "fastapi_in_deps": self._check_dependency("fastapi"),
            "django_files_present": bool(list(self.project_root.glob("**/settings.py")))
        }


def main():
    """CLI interface for framework detection"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Detect project framework type")
    parser.add_argument("--project-root", "-p", type=Path, default=Path.cwd(),
                       help="Project root directory")
    parser.add_argument("--json", "-j", action="store_true",
                       help="Output results in JSON format")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output with detailed detection info")
    
    args = parser.parse_args()
    
    detector = FrameworkDetector(args.project_root)
    framework = detector.detect_framework()
    
    if args.json:
        report = detector.generate_detection_report()
        print(json.dumps(report, indent=2))
    else:
        print(f"Detected Framework: {framework.value}")
        
        if args.verbose:
            report = detector.generate_detection_report()
            print(f"Confidence: {report['confidence']:.2%}")
            print(f"Test Command: {report['test_command']}")
            print(f"Structure Path: {report['recommended_structure']}")
            print(f"Dependency File: {report['dependency_file']}")
            
            print("\nDetection Indicators:")
            for indicator, found in report['detection_indicators'].items():
                status = "✅" if found else "❌"
                print(f"  {status} {indicator}")


if __name__ == "__main__":
    main()