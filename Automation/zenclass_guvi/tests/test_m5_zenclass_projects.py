"""
tests/test_m5_zenclass_projects.py - Comprehensive Unit and Integration Test Suite for Milestone 5.

Validates:
- ProjectSynthesizer: Slug generation, type detection (Frontend, Node, Python), directory scaffolding,
  package manifests, README.md with deployment guides, and .gitignore.
- ProjectValidator: HTMLTagValidator (stack-based balanced tag validator with void tag tolerance),
  CSS parser, JS syntax validator (node --check / Python fallback), Python syntax compiler,
  JSON validator, and validation_report.json artifact generation.
- ZenClassProjectsDriver 5-Stage Lifecycle:
  - Stage 1: Discovery & Catalog Parsing (Active, Pending, Completed Kanban columns, card attributes,
    action types, and detail modal extraction).
  - Stage 2: Local Code Synthesis in projects/<slug>/.
  - Stage 3: Local Build & Syntax Validation.
  - Stage 4: Interactive Human Pause Protocol (Requirement R2) with ANSI prompt box, audible alerts,
    and graceful headless non-interactive BLOCKED fallback.
  - Stage 5: Dynamic 13-field modal submission & confirmation verification with spelling resilience.
- Pipeline Orchestrator: run_projects_pipeline supporting limit and project_id targeting.
- State Persistence: batch records all 9 mandatory R3 fields into SQLite StateManager with
  platform="zenclass_projects" and task_category="Project".
- Zero Mock Evaluate Shims static verification in production drivers.
- Mandatory autospec=True on 100% of @patch decorators and context managers.
"""

from __future__ import annotations
import ast
import json
import os
import re
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import config
from core.browser import BrowserManager
from core.state_manager import StateManager, TaskStatus, TaskPlatform, TaskResult, TaskRecord
from core.hitl_handler import HitlHandler, GuardrailEvent, GuardrailType
from core.reporter import SummaryReporter
from drivers.base_driver import (
    BaseDriver,
    DriverError,
    AuthenticationError,
    GuardrailBlockedError,
    ElementNotFoundError,
)
from drivers.zenclass_tasks_driver import (
    ZenClassAuthenticationError,
    ZenClassMFABlockedError,
    ZENCLASS_TASK_FIELD_MAP,
    LABEL_TO_FIELD_KEY,
    ZENCLASS_URL_REGEX,
)
from solver.project_synthesizer import (
    ProjectSynthesizer,
    ProjectSpec,
    ProjectType,
    SynthesisResult,
)
from solver.project_validator import (
    ProjectValidator,
    ProjectValidationResult,
    ValidationReport,
    HTMLTagValidator,
)
from drivers.zenclass_projects_driver import (
    ZenClassProjectsDriver,
    ZenClassProjectError,
    DiscoveredProject,
    ZENCLASS_PROJECT_CONFIRMATION_REGEX,
)
from main import create_cli_parser, AutomationRunner


# =============================================================================
# 1. ProjectSynthesizer Unit Tests
# =============================================================================

class TestProjectSynthesizer(unittest.TestCase):
    """Verifies ProjectSynthesizer code generation, templates, and specs."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_synth_")
        self.synthesizer = ProjectSynthesizer(base_projects_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_slugify(self):
        """Verifies string slugification to filesystem-safe kebab-case."""
        self.assertEqual(
            ProjectSynthesizer.slugify("Full Stack E-Commerce Platform!"),
            "full-stack-e-commerce-platform"
        )
        self.assertEqual(ProjectSynthesizer.slugify("React / Node.js Capstone"), "react-nodejs-capstone")
        self.assertEqual(ProjectSynthesizer.slugify("   ___special   chars***  "), "special-chars")
        self.assertEqual(ProjectSynthesizer.slugify(""), "project")

    def test_detect_project_type(self):
        """Verifies heuristic detection of project architecture."""
        synth = self.synthesizer
        self.assertEqual(
            synth.detect_project_type("Flask Microservice", tags=["Python", "REST"]),
            ProjectType.FULLSTACK_PYTHON
        )
        self.assertEqual(
            synth.detect_project_type("MERN Stack Store", tags=["React", "Node.js", "Express"]),
            ProjectType.FULLSTACK_NODE
        )
        self.assertEqual(
            synth.detect_project_type("Interactive Portfolio", tags=["HTML", "CSS", "JavaScript"]),
            ProjectType.FRONTEND
        )

    def test_create_spec_helper(self):
        """Verifies spec helper constructs populated ProjectSpec."""
        spec = self.synthesizer.create_spec(
            project_id="proj-101",
            title="Online Bookstore",
            tags=["React", "Node"],
            description="Bookstore capstone",
        )
        self.assertEqual(spec.project_id, "proj-101")
        self.assertEqual(spec.slug, "online-bookstore")
        self.assertEqual(spec.project_type, ProjectType.FULLSTACK_NODE)
        self.assertIn("backEnd_Deployed_Url", spec.required_fields)

    def test_synthesize_frontend_project(self):
        """Verifies synthesis of complete modern frontend web application."""
        spec = ProjectSpec(
            project_id="proj-fe-1",
            title="Responsive Landing Page",
            slug="responsive-landing",
            tags=["HTML5", "CSS3", "JavaScript"],
            description="High-converting landing page.",
            project_type=ProjectType.FRONTEND,
        )
        res = self.synthesizer.synthesize(spec)
        self.assertTrue(res.success)
        self.assertEqual(res.project_type, ProjectType.FRONTEND)

        proj_path = Path(res.project_dir)
        self.assertTrue((proj_path / "index.html").exists())
        self.assertTrue((proj_path / "styles.css").exists())
        self.assertTrue((proj_path / "app.js").exists())
        self.assertTrue((proj_path / "package.json").exists())
        self.assertTrue((proj_path / "README.md").exists())
        self.assertTrue((proj_path / ".gitignore").exists())
        self.assertTrue((proj_path / "frontend" / "src" / "index.js").exists())

        # Inspect package.json
        pkg = json.loads((proj_path / "package.json").read_text())
        self.assertEqual(pkg["name"], "responsive-landing-frontend")

        # Inspect README content
        readme_txt = (proj_path / "README.md").read_text()
        self.assertIn("Responsive Landing Page", readme_txt)
        self.assertIn("Deployment Instructions", readme_txt)

    def test_synthesize_fullstack_node_project(self):
        """Verifies synthesis of complete client & Express server fullstack application."""
        spec = ProjectSpec(
            project_id="proj-node-1",
            title="E-Commerce API & Storefront",
            slug="ecommerce-fullstack",
            tags=["React", "Node.js", "Express"],
            project_type=ProjectType.FULLSTACK_NODE,
        )
        res = self.synthesizer.synthesize(spec)
        self.assertTrue(res.success)

        proj_path = Path(res.project_dir)
        self.assertTrue((proj_path / "client" / "index.html").exists())
        self.assertTrue((proj_path / "client" / "package.json").exists())
        self.assertTrue((proj_path / "server" / "server.js").exists())
        self.assertTrue((proj_path / "server" / "package.json").exists())
        self.assertTrue((proj_path / "backend" / "server.js").exists())
        self.assertTrue((proj_path / "package.json").exists())

        server_txt = (proj_path / "server" / "server.js").read_text()
        self.assertIn("express", server_txt)
        self.assertIn("/api/health", server_txt)

    def test_synthesize_fullstack_python_project(self):
        """Verifies synthesis of complete frontend and Flask backend application."""
        spec = ProjectSpec(
            project_id="proj-py-1",
            title="Analytics Dashboard",
            slug="analytics-dashboard",
            tags=["Python", "Flask"],
            project_type=ProjectType.FULLSTACK_PYTHON,
        )
        res = self.synthesizer.synthesize(spec)
        self.assertTrue(res.success)

        proj_path = Path(res.project_dir)
        self.assertTrue((proj_path / "frontend" / "index.html").exists())
        self.assertTrue((proj_path / "backend" / "app.py").exists())
        self.assertTrue((proj_path / "backend" / "requirements.txt").exists())
        self.assertTrue((proj_path / "run.py").exists())

        app_txt = (proj_path / "backend" / "app.py").read_text()
        self.assertIn("Flask", app_txt)
        self.assertIn("/api/health", app_txt)

    def test_synthesis_failure_handling(self):
        """Verifies graceful error handling and reporting when synthesis fails."""
        spec = ProjectSpec(
            project_id="proj-err",
            title="Error Project",
            slug="err-proj",
        )
        # Attempt synthesis to an invalid file path as directory
        invalid_file = Path(self.temp_dir) / "blocking_file"
        invalid_file.write_text("blocker")
        invalid_target = invalid_file / "sub_dir"

        res = self.synthesizer.synthesize(spec, target_dir=invalid_target)
        self.assertFalse(res.success)
        self.assertIsNotNone(res.error)


# =============================================================================
# 2. ProjectValidator Unit Tests
# =============================================================================

class TestProjectValidator(unittest.TestCase):
    """Verifies ProjectValidator syntax parsers and build health checks."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_val_")
        self.validator = ProjectValidator()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_html_tag_validator_valid_and_void_tags(self):
        """Verifies HTMLTagValidator accepts well-nested tags and void elements."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <link rel="stylesheet" href="style.css">
            <title>Test Page</title>
        </head>
        <body>
            <header><h1>Welcome</h1></header>
            <main>
                <img src="test.png" alt="img">
                <input type="text" placeholder="name">
                <br>
                <hr>
                <p>Hello world!</p>
            </main>
            <footer><p>&copy; 2026</p></footer>
        </body>
        </html>
        """
        val = HTMLTagValidator()
        errors = val.validate(html)
        self.assertEqual(len(errors), 0)

    def test_html_tag_validator_unclosed_and_mismatched(self):
        """Verifies HTMLTagValidator detects unclosed and mismatched tags."""
        bad_html = "<div><p>Mismatched</div></p>"
        val = HTMLTagValidator()
        errors = val.validate(bad_html)
        self.assertTrue(any("Mismatched closing tag" in e for e in errors))

        unclosed_html = "<div><span>Unclosed"
        val2 = HTMLTagValidator()
        errors2 = val2.validate(unclosed_html)
        self.assertTrue(any("Unclosed tag" in e for e in errors2))

    def test_css_validator(self):
        """Verifies CSS parser detects mismatched braces and unclosed comments."""
        valid_css = "body { margin: 0; padding: 0; } /* Comment */ h1 { color: red; }"
        self.assertEqual(len(self.validator._validate_css(valid_css)), 0)

        broken_braces = "body { margin: 0; h1 { color: red; }"
        errs = self.validator._validate_css(broken_braces)
        self.assertTrue(any("Mismatched braces" in e for e in errs))

        unclosed_comment = "body { color: blue; } /* Unclosed comment"
        errs_comment = self.validator._validate_css(unclosed_comment)
        self.assertTrue(any("Unclosed CSS comment" in e for e in errs_comment))

    def test_javascript_python_fallback_validator(self):
        """Verifies JavaScript bracket balancing and token verification."""
        valid_js = "function add(a, b) { return a + b; } console.log(add(1, 2));"
        self.assertEqual(len(self.validator._fallback_js_lint(valid_js)), 0)

        broken_js = "function broken(a { return a; }"
        errs = self.validator._fallback_js_lint(broken_js)
        self.assertTrue(len(errs) > 0)

    def test_python_syntax_validator(self):
        """Verifies Python syntax validator compiles valid code and catches syntax errors."""
        py_path = Path(self.temp_dir) / "good.py"
        py_path.write_text("def hello():\n    return 'world'\n")
        self.assertEqual(len(self.validator._validate_python(py_path)), 0)

        broken_py = Path(self.temp_dir) / "broken.py"
        broken_py.write_text("def broken_syntax(\n")
        errs = self.validator._validate_python(broken_py)
        self.assertTrue(len(errs) > 0)

    def test_full_project_validation_and_report_artifact(self):
        """Verifies complete project directory validation and validation_report.json generation."""
        proj_dir = Path(self.temp_dir) / "test_proj"
        proj_dir.mkdir(parents=True, exist_ok=True)

        (proj_dir / "index.html").write_text("<!DOCTYPE html><html><body><h1>Hi</h1></body></html>")
        (proj_dir / "styles.css").write_text("h1 { color: blue; }")
        (proj_dir / "app.js").write_text("console.log('Valid');")
        (proj_dir / "package.json").write_text('{"name": "valid-app", "version": "1.0.0"}')
        (proj_dir / "README.md").write_text("# Test Project\n\nComprehensive documentation exceeding minimum characters.")

        result = self.validator.validate_project(proj_dir)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)

        # Artifact exists and matches
        report_file = proj_dir / "validation_report.json"
        self.assertTrue(report_file.exists())
        with open(report_file, "r") as f:
            artifact = json.load(f)
        self.assertTrue(artifact["is_valid"])


# =============================================================================
# 3. ZenClassProjectsDriver Unit Tests
# =============================================================================

class TestZenClassProjectsDriver(unittest.TestCase):
    """Verifies ZenClassProjectsDriver authentication, stages 1-5, HITL, and pipeline."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_proj_driver_")
        self.state_db = os.path.join(self.temp_dir, "test_state.db")
        self.state_mgr = StateManager(db_path=self.state_db)

        self.mock_browser_mgr = MagicMock(spec=BrowserManager)
        self.mock_page = MagicMock()
        self.mock_browser_mgr.get_page.return_value = self.mock_page

        self.mock_hitl = MagicMock(spec=HitlHandler)
        self.mock_hitl.interactive = True
        self.mock_hitl.links_file = None

        self.mock_reporter = MagicMock(spec=SummaryReporter)

        self.driver = ZenClassProjectsDriver(
            browser_manager=self.mock_browser_mgr,
            state_manager=self.state_mgr,
            hitl_handler=self.mock_hitl,
            reporter=self.mock_reporter,
            projects_base_dir=self.temp_dir,
        )

    def tearDown(self):
        if self.state_mgr:
            self.state_mgr.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # Authentication & Session Tests
    # -------------------------------------------------------------------------

    def test_get_auth_token_from_local_storage(self):
        """Verifies authToken extraction from browser evaluate."""
        self.mock_page.evaluate.return_value = json.dumps({"authToken": "test-jwt-token", "exp": 9999999999})
        token = self.driver.get_auth_token()
        self.assertEqual(token, "test-jwt-token")

    def test_is_authenticated_tier1_fast_path(self):
        """Verifies Tier 1 DOM anchor check on open page."""
        self.mock_page.url = "https://v2.zenclass.in/projects"
        mock_anchor = MagicMock()
        mock_anchor.is_visible.return_value = True
        self.mock_page.query_selector.return_value = mock_anchor

        self.assertTrue(self.driver.is_authenticated())

    def test_is_authenticated_tier4_fallback(self):
        """Verifies Tier 4 returns False when no session exists."""
        self.mock_page.url = "https://v2.zenclass.in/login"
        self.mock_page.query_selector.return_value = None
        self.mock_page.evaluate.return_value = None

        self.assertFalse(self.driver.is_authenticated())

    def test_ensure_authenticated_credential_login(self):
        """Verifies visible credential login flow when unauthenticated."""
        with patch.object(self.driver, "is_authenticated", autospec=True) as mock_is_auth, \
             patch.object(self.driver, "_authenticate_credentials", autospec=True) as mock_auth:
            mock_is_auth.return_value = False
            mock_auth.return_value = True

            res = self.driver.ensure_authenticated()
            self.assertTrue(res)
            mock_auth.assert_called_once()

    # -------------------------------------------------------------------------
    # Stage 1: Discovery & Catalog Parsing Tests
    # -------------------------------------------------------------------------

    def test_stage1_discover_projects_kanban_parsing(self):
        """Verifies parsing of Active, Pending, and Completed project cards and SQLite persistence."""
        # Create mock cards
        mock_card_active = MagicMock()
        mock_card_active.get_attribute.side_effect = lambda a: "proj-101" if a == "data-project-id" else None

        mock_title_el = MagicMock()
        mock_title_el.inner_text.return_value = "E-Commerce App"
        mock_tag_el = MagicMock()
        mock_tag_el.inner_text.return_value = "React"
        mock_submit_btn = MagicMock()
        mock_submit_btn.is_visible.return_value = True
        mock_submit_btn.inner_text.return_value = "Submit"

        def qs_side_effect(sel):
            if "project-name" in sel:
                return mock_title_el
            if "primary-outlined-submit-btn" in sel:
                return mock_submit_btn
            return None

        mock_card_active.query_selector.side_effect = qs_side_effect
        mock_card_active.query_selector_all.side_effect = lambda sel: [mock_tag_el] if "common-tags" in sel else []

        def page_qsa(sel):
            if "itemactive-Project" in sel:
                return [mock_card_active]
            return []

        self.mock_page.query_selector_all.side_effect = page_qsa

        with patch.object(self.driver, "navigate_to_projects", autospec=True):
            projects = self.driver.discover_projects()

        self.assertEqual(len(projects), 1)
        p = projects[0]
        self.assertEqual(p.project_id, "proj-101")
        self.assertEqual(p.title, "E-Commerce App")
        self.assertEqual(p.column, "active")
        self.assertEqual(p.action_type, "SUBMIT")
        self.assertIn("React", p.tags)

        # Verify R3 SQLite StateManager persistence
        task = self.state_mgr.get_task("proj-101")
        self.assertIsNotNone(task)
        self.assertEqual(task.platform, TaskPlatform.ZENCLASS_PROJECTS.value)
        self.assertEqual(task.task_category, "Project")
        self.assertEqual(task.title, "E-Commerce App")
        self.assertEqual(task.status, TaskStatus.PENDING.value)

    def test_stage1_extract_project_details_modal(self):
        """Verifies detail modal extraction and dismissal."""
        project = DiscoveredProject(project_id="proj-201", title="Social Network", column="active")
        mock_card = MagicMock()
        mock_view_btn = MagicMock()
        mock_card.query_selector.return_value = mock_view_btn
        project.raw_element = mock_card

        mock_modal = MagicMock()
        mock_content = MagicMock()
        mock_content.inner_text.return_value = "Build a scalable social network."
        mock_modal.query_selector.side_effect = lambda sel: mock_content if "view-task-content" in sel else MagicMock()
        mock_modal.query_selector_all.return_value = []
        self.mock_page.query_selector.return_value = mock_modal

        details = self.driver.extract_project_details(project)
        self.assertEqual(details["project_id"], "proj-201")
        self.assertEqual(details["content"], "Build a scalable social network.")
        mock_view_btn.click.assert_called_once()

    # -------------------------------------------------------------------------
    # Stage 2 & 3: Local Code Synthesis & Validation Tests
    # -------------------------------------------------------------------------

    def test_stage2_synthesize_project(self):
        """Verifies local code preparation in projects/<slug>/ and StateManager update."""
        self.state_mgr.record_task(
            task_id="proj-synth-1",
            platform="zenclass_projects",
            task_category="Project",
            title="Chat Platform",
            status="pending",
        )
        project = DiscoveredProject(
            project_id="proj-synth-1",
            title="Chat Platform",
            column="active",
            tags=["Node.js", "Express", "Socket.io"],
        )
        res = self.driver.synthesize_project(project)
        self.assertTrue(res.success)
        self.assertTrue((res.project_dir / "README.md").exists())


        task = self.state_mgr.get_task("proj-synth-1")
        self.assertEqual(task.status, TaskStatus.IN_PROGRESS.value)
        self.assertEqual(task.next_action, "validation")

    def test_stage3_validate_project_code(self):
        """Verifies local build verification and StateManager transitions."""
        # Create a valid project directory
        proj_dir = Path(self.temp_dir) / "valid-test-proj"
        proj_dir.mkdir(parents=True, exist_ok=True)
        (proj_dir / "index.html").write_text("<!DOCTYPE html><html><body><p>Test</p></body></html>")
        (proj_dir / "styles.css").write_text("p { color: green; }")
        (proj_dir / "app.js").write_text("console.log('Ok');")
        (proj_dir / "package.json").write_text('{"name": "valid", "version": "1.0.0"}')
        (proj_dir / "README.md").write_text("# Readme exceeding minimum requirement threshold.")

        # Record initial task state
        self.state_mgr.record_task(
            task_id="proj-val-1",
            platform="zenclass_projects",
            task_category="Project",
            title="Valid Project",
            status="in_progress",
        )

        res = self.driver.validate_project_code(proj_dir, project_id="proj-val-1")
        self.assertTrue(res.is_valid)

        task = self.state_mgr.get_task("proj-val-1")
        self.assertEqual(task.result, "Local validation passed")
        self.assertEqual(task.next_action, "hitl_pause")

    # -------------------------------------------------------------------------
    # Stage 4: Interactive Human Pause Protocol (Requirement R2)
    # -------------------------------------------------------------------------

    def test_stage4_hitl_pause_with_user_inputs(self):
        """Verifies HITL pause transitions to BLOCKED then to IN_PROGRESS upon input."""
        project = DiscoveredProject(project_id="proj-hitl-1", title="Payment Gateway", column="active")
        self.state_mgr.record_task(
            task_id="proj-hitl-1",
            platform="zenclass_projects",
            task_category="Project",
            title="Payment Gateway",
            status="in_progress",
        )

        user_urls = {
            "github_Url": "https://github.com/test/gateway",
            "frontEnd_Deployed_Url": "https://gateway.vercel.app",
        }
        self.mock_hitl.request_project_links.return_value = user_urls

        res = self.driver.handle_hitl_pause(
            project=project,
            local_code_dir=Path(self.temp_dir) / "gateway",
            user_inputs=user_urls,
        )
        self.assertEqual(res, user_urls)

        task = self.state_mgr.get_task("proj-hitl-1")
        self.assertEqual(task.status, TaskStatus.IN_PROGRESS.value)
        self.assertEqual(task.result, "COLLECTED_PROJECT_URLS")
        self.assertEqual(task.next_action, "SUBMIT_PROJECT")
        self.assertEqual(task.metadata["collected_links"]["github_Url"], "https://github.com/test/gateway")

    def test_stage4_hitl_pause_non_interactive_fallback(self):
        """Verifies non-interactive headless run gracefully marks task as BLOCKED without crashing."""
        project = DiscoveredProject(project_id="proj-block-1", title="Cloud Storage", column="active")
        self.state_mgr.record_task(
            task_id="proj-block-1",
            platform="zenclass_projects",
            task_category="Project",
            title="Cloud Storage",
            status="in_progress",
        )

        self.mock_hitl.request_project_links.side_effect = RuntimeError(
            "Non-interactive run cannot supply project links..."
        )

        res = self.driver.handle_hitl_pause(
            project=project,
            local_code_dir=Path(self.temp_dir) / "storage",
        )
        self.assertIsNone(res)

        task = self.state_mgr.get_task("proj-block-1")
        self.assertEqual(task.status, TaskStatus.BLOCKED.value)
        self.assertEqual(task.result, TaskResult.AWAITING_INPUT.value)
        self.assertEqual(task.failure_reason, "Awaiting user repository hosting and deployment URLs")
        self.assertEqual(task.next_action, "PROVIDE_PROJECT_URLS")

    # -------------------------------------------------------------------------
    # Stage 5: Dynamic Modal Submission Tests
    # -------------------------------------------------------------------------

    def test_stage5_dynamic_modal_submission_positive_confirmation(self):
        """Verifies typing deliverable links, modal submission, and confirmation verification."""
        self.state_mgr.record_task(
            task_id="proj-sub-1",
            platform="zenclass_projects",
            task_category="Project",
            title="Task Manager",
            status="in_progress",
        )

        # Mock submit button on card
        mock_card_btn = MagicMock()
        # Mock submission modal and fields
        mock_modal = MagicMock()
        mock_modal.is_visible.return_value = True

        mock_wrap_gh = MagicMock()
        mock_lbl_gh = MagicMock()
        mock_lbl_gh.inner_text.return_value = "Github URL"
        mock_inp_gh = MagicMock()
        mock_wrap_gh.query_selector.side_effect = lambda s: mock_lbl_gh if "label" in s else mock_inp_gh

        mock_confirm_btn = MagicMock()
        mock_popup = MagicMock()
        mock_popup_txt = MagicMock()
        mock_popup_txt.inner_text.return_value = "Project Submitted Successfully"

        def qs_side(sel):
            if "submit-form-container-web" in sel:
                return mock_modal
            if "primary-btn" in sel or "button" in sel:
                return mock_confirm_btn
            if "sucess-popup-text" in sel:
                return mock_popup_txt
            if "validation-error" in sel:
                return None
            return mock_card_btn


        self.mock_page.query_selector.side_effect = qs_side
        self.mock_page.query_selector_all.return_value = [mock_wrap_gh]
        self.mock_page.wait_for_selector.return_value = mock_popup

        sub_res = self.driver.submit_project(
            project_id="proj-sub-1",
            deliverable_urls={"github_Url": "https://github.com/devsh/taskmgr"},
        )
        self.assertTrue(sub_res["success"])
        mock_inp_gh.fill.assert_called_with("https://github.com/devsh/taskmgr")
        mock_confirm_btn.click.assert_called_once()

        task = self.state_mgr.get_task("proj-sub-1")
        self.assertEqual(task.status, TaskStatus.COMPLETED.value)
        self.assertEqual(task.result, TaskResult.SUBMITTED.value)
        self.assertIsNone(task.failure_reason)

    def test_stage5_dynamic_modal_submission_failure_records_failed(self):
        """Verifies platform error or missing modal records FAILED state."""
        self.state_mgr.record_task(
            task_id="proj-fail-1",
            platform="zenclass_projects",
            task_category="Project",
            title="Failed Proj",
            status="in_progress",
        )
        self.mock_page.query_selector.return_value = None  # Modal not found

        sub_res = self.driver.submit_project(
            project_id="proj-fail-1",
            deliverable_urls={"github_Url": "https://github.com/test/repo"},
        )
        self.assertFalse(sub_res["success"])

        task = self.state_mgr.get_task("proj-fail-1")
        self.assertEqual(task.status, TaskStatus.FAILED.value)
        self.assertEqual(task.result, TaskResult.SUBMISSION_FAILED.value)

    # -------------------------------------------------------------------------
    # Pipeline Orchestration Tests
    # -------------------------------------------------------------------------

    def test_run_projects_pipeline_with_limit_and_blocked(self):
        """Verifies end-to-end pipeline execution with limit and external quiz blocking."""
        with patch.object(self.driver, "ensure_authenticated", autospec=True) as mock_auth, \
             patch.object(self.driver, "discover_projects", autospec=True) as mock_disc, \
             patch.object(self.driver, "extract_project_details", autospec=True) as mock_det, \
             patch.object(self.driver, "synthesize_project", autospec=True) as mock_syn, \
             patch.object(self.driver, "validate_project_code", autospec=True) as mock_val, \
             patch.object(self.driver, "handle_hitl_pause", autospec=True) as mock_hitl, \
             patch.object(self.driver, "submit_project", autospec=True) as mock_sub:

            mock_auth.return_value = True
            p1 = DiscoveredProject(project_id="proj-p1", title="P1", column="active", action_type="SUBMIT")
            p2 = DiscoveredProject(project_id="proj-p2", title="Quiz", column="active", action_type="ATTEND")
            p3 = DiscoveredProject(project_id="proj-p3", title="P3", column="active", action_type="SUBMIT")
            mock_disc.return_value = [p1, p2, p3]

            synth_res = SynthesisResult(
                success=True,
                project_dir=Path(self.temp_dir) / "p1",
                project_type=ProjectType.FRONTEND,
                files_created=[],
                summary="Ok",
            )
            mock_syn.return_value = synth_res
            mock_val.return_value = ProjectValidationResult(is_valid=True, project_dir="p1")
            mock_hitl.return_value = {"github_Url": "https://github.com/test/p1"}
            mock_sub.return_value = {"success": True, "project_id": "proj-p1"}

            # Limit = 2
            summary = self.driver.run_projects_pipeline(limit=2)

            self.assertEqual(summary["total_discovered"], 3)
            self.assertEqual(summary["queue_size"], 2)
            self.assertEqual(summary["completed"], 1)
            self.assertEqual(summary["blocked"], 1)  # p2 is ATTEND
            self.assertEqual(summary["failed"], 0)


# =============================================================================
# 4. Milestone 5 Integrity, Static Compliance, and CLI Tests
# =============================================================================

class TestMilestone5IntegrityAndExports(unittest.TestCase):
    """Verifies exports, zero mock evaluate shims, and autospec=True enforcement."""

    def test_solver_and_driver_exports(self):
        """Verifies all required symbols are cleanly exported by solver and drivers."""
        import solver
        self.assertTrue(hasattr(solver, "ProjectSynthesizer"))
        self.assertTrue(hasattr(solver, "ProjectValidator"))
        self.assertTrue(hasattr(solver, "ValidationReport"))
        self.assertTrue(hasattr(solver, "HTMLTagValidator"))

        import drivers
        self.assertTrue(hasattr(drivers, "ZenClassProjectsDriver"))
        self.assertTrue(hasattr(drivers, "ZenClassProjectError"))
        self.assertTrue(hasattr(drivers, "DiscoveredProject"))
        self.assertTrue(hasattr(drivers, "ZENCLASS_PROJECT_CONFIRMATION_REGEX"))

    def test_zero_mock_evaluate_shims_in_driver(self):
        """Audit requirement: ZenClassProjectsDriver contains zero mock evaluate shims or mock imports."""
        driver_file = Path(PROJECT_ROOT) / "drivers" / "zenclass_projects_driver.py"
        content = driver_file.read_text(encoding="utf-8")

        # Must not contain isinstance(*evaluate, (MagicMock, Mock))
        self.assertFalse(re.findall(r"isinstance\([^,]+evaluate,\s*(?:MagicMock|Mock)\)", content))
        # Must not import unittest.mock in production driver
        self.assertFalse(re.findall(r"from unittest\.mock", content))
        self.assertFalse(re.findall(r"import unittest\.mock", content))

    def test_cli_parser_has_zenclass_projects(self):
        """Verifies run-zenclass-projects subparser exists with correct options."""
        parser = create_cli_parser()
        args = parser.parse_args(["run-zenclass-projects", "--project-id", "proj-999", "--skip-synthesis"])
        self.assertEqual(args.command, "run-zenclass-projects")
        self.assertEqual(args.project_id, "proj-999")
        self.assertTrue(args.skip_synthesis)

    def test_all_patch_calls_enforce_autospec_true(self):
        """
        Integrity Mandate Check:
        Inspects this test file's AST to guarantee that 100% of @patch decorators
        and patch(...) context managers explicitly specify autospec=True.
        """
        test_file = Path(__file__).resolve()
        tree = ast.parse(test_file.read_text(encoding="utf-8"))

        patches_found = 0
        for node in ast.walk(tree):
            is_patch_call = False
            # Check decorator: @patch(...) or @patch.object(...)
            # Check context manager: with patch(...) or with patch.object(...)
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id in ("patch",):
                    is_patch_call = True
                elif isinstance(func, ast.Attribute) and func.attr in ("patch", "object"):
                    if isinstance(func.value, ast.Name) and func.value.id in ("patch",):
                        is_patch_call = True

            if is_patch_call:
                patches_found += 1
                has_autospec = False
                for kw in node.keywords:
                    if kw.arg == "autospec":
                        if isinstance(kw.value, ast.Constant) and kw.value.value is True:
                            has_autospec = True
                        elif isinstance(kw.value, ast.Name) and kw.value.id == "True":
                            has_autospec = True
                self.assertTrue(
                    has_autospec,
                    f"Integrity Violation: patch at line {node.lineno} does NOT enforce autospec=True!"
                )

        self.assertGreater(patches_found, 0, "Expected at least one @patch call in test suite.")
        print(f"\n[Audit Passed] Verified {patches_found} @patch call(s) in test suite all enforce autospec=True.")


if __name__ == "__main__":
    unittest.main()
