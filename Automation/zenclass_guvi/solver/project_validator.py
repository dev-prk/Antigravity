"""
solver/project_validator.py - Automated Local Project Build and Syntax Validator.

Validates synthesized project health before prompting the user (Requirement R2):
- HTML balanced tags and semantic structure
- CSS syntax and brace matching
- JavaScript syntax check (node --check with robust Python fallback)
- Python compilation check (py_compile / ast)
- JSON validity (package.json)
- Generates structured validation_report.json artifact
"""

from __future__ import annotations
import ast
import json
import logging
import os
import py_compile
import re
import subprocess
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

logger = logging.getLogger("solver.project_validator")


class HTMLTagValidator(HTMLParser):
    """Stack-based HTML validator checking balanced tags and proper nesting."""
    VOID_TAGS: Set[str] = {
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr"
    }

    def __init__(self) -> None:
        super().__init__()
        self.stack: List[Tuple[str, int]] = []
        self.errors: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        tag_lower = tag.lower()
        if tag_lower not in self.VOID_TAGS:
            line_no = self.getpos()[0]
            self.stack.append((tag_lower, line_no))

    def handle_endtag(self, tag: str) -> None:
        tag_lower = tag.lower()
        if tag_lower in self.VOID_TAGS:
            return
        line_no = self.getpos()[0]
        if not self.stack:
            self.errors.append(f"Unexpected closing tag </{tag_lower}> at line {line_no}")
            return
        last_tag, opened_line = self.stack.pop()
        if last_tag != tag_lower:
            self.errors.append(
                f"Mismatched closing tag: expected </{last_tag}> (opened at line {opened_line}), "
                f"got </{tag_lower}> at line {line_no}"
            )

    def validate(self, html_text: str) -> List[str]:
        """Validates HTML string and returns list of syntax/balance errors."""
        self.stack.clear()
        self.errors.clear()
        try:
            self.feed(html_text)
            while self.stack:
                unclosed, opened_line = self.stack.pop()
                self.errors.append(f"Unclosed tag <{unclosed}> opened at line {opened_line}")
        except Exception as e:
            self.errors.append(f"HTML parsing exception: {e}")
        return list(self.errors)


@dataclass
class ProjectValidationResult:
    """Artifact detailing local project build and syntax verification."""
    is_valid: bool
    project_dir: str
    checked_files: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "project_dir": self.project_dir,
            "checked_files": self.checked_files,
            "errors": self.errors,
            "warnings": self.warnings,
            "details": self.details,
        }


# Canonical alias for naming flexibility
ValidationReport = ProjectValidationResult


class ProjectValidator:
    """Automated validator verifying project syntax and build health."""

    def __init__(self, node_executable: str = "node") -> None:
        self.node_exec = node_executable

    def validate_project(self, project_dir: Union[str, Path]) -> ProjectValidationResult:
        """Inspects all project source files and compiles comprehensive report."""
        p_dir = Path(project_dir).resolve()
        checked_files: List[str] = []
        errors: List[str] = []
        warnings: List[str] = []
        details: Dict[str, Any] = {}

        if not p_dir.exists() or not p_dir.is_dir():
            return ProjectValidationResult(
                is_valid=False,
                project_dir=str(p_dir),
                errors=[f"Project directory does not exist: {p_dir}"]
            )

        # 1. Validate HTML files
        for html_file in sorted(p_dir.rglob("*.html")):
            rel_name = str(html_file.relative_to(p_dir))
            checked_files.append(rel_name)
            html_content = html_file.read_text(encoding="utf-8", errors="replace")
            validator = HTMLTagValidator()
            html_errors = validator.validate(html_content)
            if html_errors:
                errors.extend([f"[{rel_name}] {e}" for e in html_errors])
            details[rel_name] = {
                "status": "error" if html_errors else "pass",
                "errors": html_errors
            }

        # 2. Validate CSS files
        for css_file in sorted(p_dir.rglob("*.css")):
            rel_name = str(css_file.relative_to(p_dir))
            checked_files.append(rel_name)
            css_content = css_file.read_text(encoding="utf-8", errors="replace")
            css_errors = self._validate_css(css_content)
            if css_errors:
                errors.extend([f"[{rel_name}] {e}" for e in css_errors])
            details[rel_name] = {
                "status": "error" if css_errors else "pass",
                "errors": css_errors
            }

        # 3. Validate JSON files (excluding validation_report.json)
        for json_file in sorted(p_dir.rglob("*.json")):
            if json_file.name == "validation_report.json":
                continue
            rel_name = str(json_file.relative_to(p_dir))
            checked_files.append(rel_name)
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    json.load(f)
                details[rel_name] = {"status": "pass"}
            except Exception as e:
                err = f"[{rel_name}] Malformed JSON: {e}"
                errors.append(err)
                details[rel_name] = {"status": "error", "errors": [str(e)]}

        # 4. Validate JavaScript files
        for js_file in sorted(p_dir.rglob("*.js")):
            rel_name = str(js_file.relative_to(p_dir))
            checked_files.append(rel_name)
            js_errors = self._validate_javascript(js_file)
            if js_errors:
                errors.extend([f"[{rel_name}] {e}" for e in js_errors])
            details[rel_name] = {
                "status": "error" if js_errors else "pass",
                "errors": js_errors
            }

        # 5. Validate Python files
        for py_file in sorted(p_dir.rglob("*.py")):
            rel_name = str(py_file.relative_to(p_dir))
            checked_files.append(rel_name)
            py_errors = self._validate_python(py_file)
            if py_errors:
                errors.extend([f"[{rel_name}] {e}" for e in py_errors])
            details[rel_name] = {
                "status": "error" if py_errors else "pass",
                "errors": py_errors
            }

        # 6. Verify README.md
        readme_path = p_dir / "README.md"
        if not readme_path.exists():
            warnings.append("README.md is missing from project root.")
        else:
            checked_files.append("README.md")
            if len(readme_path.read_text(encoding="utf-8").strip()) < 50:
                warnings.append("README.md is shorter than recommended (less than 50 characters).")

        is_valid = (len(errors) == 0)
        result = ProjectValidationResult(
            is_valid=is_valid,
            project_dir=str(p_dir),
            checked_files=checked_files,
            errors=errors,
            warnings=warnings,
            details=details,
        )

        # Write validation artifact
        report_file = p_dir / "validation_report.json"
        try:
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(result.to_dict(), f, indent=2)
        except Exception as e:
            logger.warning(f"Could not write validation report artifact: {e}")

        return result

    def _validate_css(self, css_text: str) -> List[str]:
        """Validates CSS brace matching and unclosed comments."""
        errors: List[str] = []
        open_braces = css_text.count("{")
        close_braces = css_text.count("}")
        if open_braces != close_braces:
            errors.append(f"Mismatched braces: found {open_braces} '{{' and {close_braces} '}}'")

        if "/*" in css_text:
            open_comments = css_text.count("/*")
            close_comments = css_text.count("*/")
            if open_comments != close_comments:
                errors.append(f"Unclosed CSS comment: found {open_comments} '/*' and {close_comments} '*/'")

        return errors

    def _validate_javascript(self, js_path: Path) -> List[str]:
        """Validates JS syntax with node --check, falling back to Python-based bracket check."""
        try:
            res = subprocess.run(
                [self.node_exec, "--check", str(js_path)],
                capture_output=True,
                text=True,
                timeout=5.0
            )
            if res.returncode != 0:
                return [f"Node syntax check failed: {res.stderr.strip()}"]
            return []
        except (FileNotFoundError, subprocess.SubprocessError):
            return self._fallback_js_lint(js_path.read_text(encoding="utf-8", errors="replace"))

    def _fallback_js_lint(self, js_code: str) -> List[str]:
        """Robust Python-based bracket/brace/parenthesis balancer."""
        errors: List[str] = []
        # Strip single-line and multi-line comments
        clean_code = re.sub(r"//.*", "", js_code)
        clean_code = re.sub(r"/\*[\s\S]*?\*/", "", clean_code)

        stack: List[Tuple[str, int]] = []
        pairs = {')': '(', '}': '{', ']': '['}
        for idx, char in enumerate(clean_code):
            if char in "({[":
                stack.append((char, idx))
            elif char in ")}]":
                if not stack:
                    return [f"Unexpected closing '{char}' at index {idx}"]
                top, _ = stack.pop()
                if top != pairs[char]:
                    return [f"Mismatched bracket '{top}' closed by '{char}' at index {idx}"]
        if stack:
            unclosed, idx = stack[-1]
            return [f"Unclosed '{unclosed}' at index {idx}"]
        return errors

    def _validate_python(self, py_path: Path) -> List[str]:
        """Validates Python file compilation and AST parse."""
        try:
            py_compile.compile(str(py_path), doraise=True)
            # Also AST parse for safety
            ast.parse(py_path.read_text(encoding="utf-8"))
            return []
        except py_compile.PyCompileError as e:
            return [f"Python compile error: {e}"]
        except Exception as e:
            return [f"Python syntax error: {e}"]
