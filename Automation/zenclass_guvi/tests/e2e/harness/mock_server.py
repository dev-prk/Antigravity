"""
Mock Platform HTTP Server for Guvi and ZenClass Opaque-Box E2E Testing.
Runs in a background thread and serves authentic HTML pages and API responses.
"""

import http.server
import json
import socketserver
import threading
import urllib.parse
from typing import Dict, Any, Optional

from tests.e2e.harness.dom_fixtures import (
    GUVI_LOGIN_HTML,
    GUVI_CODEKATA_TABLE_HTML,
    GUVI_WORKSPACE_HTML,
    ZENCLASS_LOGIN_HTML,
    ZENCLASS_TASKS_HTML,
    ZENCLASS_SUBMISSION_MODAL_HTML,
    ZENCLASS_PROJECTS_HTML
)


class MockPlatformHandler(http.server.BaseHTTPRequestHandler):
    """Handles requests for simulated Guvi and ZenClass endpoints."""

    def log_message(self, format, *args):
        # Suppress noisy standard HTTP logs in test output
        pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ("/sign-in/", "/sign-in"):
            self._send_html(GUVI_LOGIN_HTML)
        elif path in ("/code-kata/", "/code-kata"):
            self._send_html(GUVI_CODEKATA_TABLE_HTML)
        elif path.startswith("/code-kata/"):
            self._send_html(GUVI_WORKSPACE_HTML)
        elif path in ("/login", "/login/"):
            self._send_html(ZENCLASS_LOGIN_HTML)
        elif path in ("/tasks", "/tasks/"):
            self._send_html(ZENCLASS_TASKS_HTML)
        elif path in ("/projects", "/projects/"):
            self._send_html(ZENCLASS_PROJECTS_HTML)
        elif path == "/health":
            self._send_json({"status": "healthy"})
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len) if content_len > 0 else b""
        data = {}
        try:
            if post_body:
                data = json.loads(post_body.decode("utf-8"))
        except Exception:
            # Maybe form urlencoded
            data = urllib.parse.parse_qs(post_body.decode("utf-8"))

        path = urllib.parse.urlparse(self.path).path

        # Guvi endpoints
        if "usercheck.php" in path:
            email = data.get("emails") or data.get("email", [""])[0] if isinstance(data, dict) else ""
            pwd = data.get("password", "")
            if email == "devsh.pareek@gmail.com" and pwd == "Dev@99#$%esh":
                self._send_json({
                    "status": "success",
                    "authToken": "auth:test_token_guvi_12345",
                    "cusername": "Devesh Pareek",
                    "userpoints": 2195
                })
            elif email == "mfa@guvi.in":
                self._send_json({"status": "mfa", "access": "activate"})
            else:
                self._send_json({"status": "fail", "message": "Incorrect Email or Password"}, status=401)

        elif "code-kata/question/run" in path:
            self._send_json({
                "status": "success",
                "output": "odd",
                "expected": "odd",
                "testCases": [{"id": 1, "status": "Correct Answer"}]
            })

        elif "code-kata/question/submit" in path:
            self._send_json({
                "status": "success",
                "message": "Solved!",
                "earned_points": 30,
                "completed": True
            })

        # ZenClass endpoints
        elif path in ("/login/", "/api/login"):
            email = data.get("email", "")
            pwd = data.get("password", "")
            if email == "devsh.pareek@gmail.com" and pwd == "Dev@99#$%esh":
                self._send_json({
                    "status": "success",
                    "authToken": "zen_token_abc_67890",
                    "userRole": "student",
                    "userCourse": "MERN"
                })
            elif email == "mfa@zenclass.in":
                self._send_json({"action": "mfaRequired", "status": "challenge"})
            else:
                self._send_json({"message": "*Incorrect email or password!"}, status=401)

        elif "task-submit" in path or "task-resubmit" in path:
            self._send_json({
                "status": "success",
                "message": "Task Submitted Suceessfully",
                "submissionId": data.get("submissionId", "sub-101")
            })

        elif "submit-project" in path or "re-submit-project" in path:
            self._send_json({
                "status": "success",
                "message": "Project submitted successfully",
                "submissionId": data.get("submissionId", "proj-sub-501")
            })

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Endpoint Not Found")

    def _send_html(self, html_text: str, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        body = html_text.encode("utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, data: Dict[str, Any], status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        body = json.dumps(data).encode("utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class MockPlatformServer:
    """Threaded local HTTP server for testing."""

    def __init__(self, port: int = 0):
        self.server = socketserver.TCPServer(("127.0.0.1", port), MockPlatformHandler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True

    def start(self):
        self.thread.start()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()

    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
