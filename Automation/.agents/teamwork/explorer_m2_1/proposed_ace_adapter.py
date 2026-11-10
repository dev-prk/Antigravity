"""
solver/ace_adapter.py - Playwright Ace Editor Keyboard and API Adapter.

Provides reliable code injection, retrieval, and readiness synchronization for
Ace Editor instances (specifically div#editor.ace_editor on Guvi CodeKata).

Guvi CodeKata uses Ajax.org Cloud9 Editor (Ace Editor), NOT Monaco Editor.
Ace Editor does not accept standard synthetic ClipboardEvent('paste') events,
requiring Chrome DevTools Protocol (CDP) native keyboard text insertion
(Input.insertText) with direct JavaScript API fallback (ace.edit().setValue()).
"""

import logging
import sys
import time
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Canonical DOM Selectors for Ace Editor on Guvi CodeKata
ACE_EDITOR_CONTAINER = "div#editor.ace_editor, #editor.ace_editor, #editor"
ACE_TEXT_INPUT = "#editor textarea.ace_text-input, textarea.ace_text-input"
ACE_LINE_LAYER = "#editor .ace_line, .ace_layer.ace_text-layer .ace_line"


class AceEditorAdapter:
    """
    Adapter for interacting with Ace Editor instances via Playwright.
    Combines CDP native keyboard events with JavaScript DOM API fallbacks.
    """

    def __init__(
        self,
        editor_selector: str = "#editor",
        textarea_selector: str = "#editor textarea.ace_text-input",
    ):
        self.editor_selector = editor_selector
        self.textarea_selector = textarea_selector

    def wait_for_ready(self, page: Any, timeout: float = 10.0) -> bool:
        """
        Waits until Ace Editor DOM elements and JavaScript runtime are initialized.

        Args:
            page: Playwright Page instance.
            timeout: Maximum seconds to wait (default: 10.0s).

        Returns:
            bool: True if editor is ready for input, False on timeout.
        """
        start_time = time.time()
        timeout_ms = int(timeout * 1000)

        # 1. Check for mock/headless test environments lacking locator API
        if not hasattr(page, "wait_for_selector"):
            logger.debug("Page object does not support wait_for_selector; assuming ready.")
            return True

        try:
            # 2. Wait for container and input textarea to be visible in DOM
            page.wait_for_selector(self.textarea_selector, state="attached", timeout=timeout_ms)

            # 3. Wait for Ace JavaScript API or environment binding
            remaining_ms = max(500, int((timeout - (time.time() - start_time)) * 1000))
            page.wait_for_function(
                """() => {
                    const el = document.querySelector('#editor');
                    if (!el) return false;
                    const hasAceGlobal = typeof window.ace !== 'undefined';
                    const hasEnvEditor = el.env && typeof el.env.editor !== 'undefined';
                    const hasLines = el.querySelectorAll('.ace_line').length > 0;
                    return hasAceGlobal || hasEnvEditor || hasLines;
                }""",
                timeout=remaining_ms
            )
            return True
        except Exception as e:
            logger.warning("Ace Editor readiness wait timed out or failed: %s", e)
            # Check if at least the textarea is present
            try:
                el = page.query_selector(self.textarea_selector)
                return el is not None
            except Exception:
                return False

    def inject_code(self, page: Any, code: str, verify: bool = True) -> bool:
        """
        Injects code into Ace Editor via Playwright CDP keyboard events.
        Falls back to direct JavaScript ace.edit().setValue() if CDP is unavailable.

        Protocol:
          1. Focus #editor textarea.ace_text-input
          2. Select All (Meta+A on macOS, Control+A on Linux/Windows)
          3. Clear buffer (Backspace)
          4. Insert code via page.keyboard.insert_text(code) (CDP Input.insertText)
          5. Verify and fallback to JS API if necessary

        Args:
            page: Playwright Page instance.
            code: Source code string to insert.
            verify: Whether to verify injected code against editor buffer.

        Returns:
            bool: True if code successfully injected, False otherwise.
        """
        if not code:
            code = ""

        # Normalize line endings
        normalized_code = code.replace("\r\n", "\n")

        # Attempt Primary: CDP Native Keyboard Injection
        cdp_success = self._inject_via_keyboard(page, normalized_code)

        if not cdp_success:
            logger.info("CDP keyboard insertion did not succeed, attempting JavaScript direct API fallback.")
            js_success = self._inject_via_js_api(page, normalized_code)
            if not js_success:
                logger.error("Both CDP keyboard and JS API injection failed.")
                return False

        # Verification step
        if verify:
            current = self.get_code(page)
            if current.strip() != normalized_code.strip():
                logger.warning(
                    "Injected code mismatch detected (len=%d vs expected=%d). Forcing JS API setValue().",
                    len(current),
                    len(normalized_code)
                )
                self._inject_via_js_api(page, normalized_code)
                current = self.get_code(page)
                if current.strip() != normalized_code.strip():
                    logger.error("Verification failed after JS API fallback.")
                    return False

        return True

    def _inject_via_keyboard(self, page: Any, code: str) -> bool:
        """Executes the 4-step CDP keyboard injection sequence."""
        if not hasattr(page, "keyboard") or page.keyboard is None:
            return False

        try:
            # Step 1: Click and focus the textarea
            if hasattr(page, "click"):
                page.click(self.textarea_selector, timeout=5000)
            elif hasattr(page, "focus"):
                page.focus(self.textarea_selector)

            # Step 2: Select All (Meta+A on macOS, Control+A on Linux/Windows)
            modifier = "Meta" if sys.platform == "darwin" else "Control"
            page.keyboard.press(f"{modifier}+A")

            # Step 3: Clear buffer with Backspace
            page.keyboard.press("Backspace")

            # Step 4: Insert text using CDP native input stream
            # Playwright insert_text triggers CDP Input.insertText which produces trusted OS input
            page.keyboard.insert_text(code)
            return True
        except Exception as e:
            logger.debug("Keyboard injection raised exception: %s", e)
            return False

    def _inject_via_js_api(self, page: Any, code: str) -> bool:
        """Directly injects code via window.ace or element.env.editor in JavaScript."""
        if not hasattr(page, "evaluate"):
            return False

        try:
            res = page.evaluate(
                """([editorId, newCode]) => {
                    try {
                        // 1. Try global ace.edit(editorId)
                        if (typeof window.ace !== 'undefined' && typeof window.ace.edit === 'function') {
                            const editor = window.ace.edit(editorId);
                            if (editor) {
                                editor.setValue(newCode, 1);
                                return true;
                            }
                        }
                        // 2. Try element.env.editor property attached by Ace
                        const el = document.getElementById(editorId) || document.querySelector('#editor');
                        if (el && el.env && el.env.editor) {
                            el.env.editor.setValue(newCode, 1);
                            return true;
                        }
                        // 3. Fallback: update textarea value and dispatch input event
                        const ta = el ? el.querySelector('textarea.ace_text-input') : document.querySelector('textarea.ace_text-input');
                        if (ta) {
                            ta.value = newCode;
                            ta.dispatchEvent(new Event('input', { bubbles: true }));
                            return true;
                        }
                        return false;
                    } catch (e) {
                        return false;
                    }
                }""",
                ["editor", code]
            )
            return bool(res)
        except Exception as e:
            logger.warning("JavaScript API injection failed: %s", e)
            return False

    def get_code(self, page: Any) -> str:
        """
        Retrieves current code from Ace Editor buffer.

        Strategies:
          1. window.ace.edit('editor').getValue()
          2. document.getElementById('editor').env.editor.getValue()
          3. Concatenate all div.ace_line text nodes
          4. textarea.value fallback
        """
        if not hasattr(page, "evaluate"):
            return ""

        try:
            code = page.evaluate(
                """(editorId) => {
                    try {
                        // Strategy 1: Global ace.edit()
                        if (typeof window.ace !== 'undefined' && typeof window.ace.edit === 'function') {
                            const editor = window.ace.edit(editorId);
                            if (editor && typeof editor.getValue === 'function') {
                                return editor.getValue();
                            }
                        }
                        // Strategy 2: DOM env.editor
                        const el = document.getElementById(editorId) || document.querySelector('#editor');
                        if (el && el.env && el.env.editor && typeof el.env.editor.getValue === 'function') {
                            return el.env.editor.getValue();
                        }
                        // Strategy 3: Concatenate visible ace lines
                        const lines = document.querySelectorAll('#editor .ace_line, .ace_layer.ace_text-layer .ace_line');
                        if (lines && lines.length > 0) {
                            return Array.from(lines).map(l => l.textContent || '').join('\\n');
                        }
                        // Strategy 4: Textarea value
                        const ta = document.querySelector('textarea.ace_text-input');
                        if (ta && ta.value) {
                            return ta.value;
                        }
                        return '';
                    } catch (e) {
                        return '';
                    }
                }""",
                "editor"
            )
            return code or ""
        except Exception as e:
            logger.debug("Failed to get editor code: %s", e)
            return ""


# Default singleton instance
_default_adapter = AceEditorAdapter()


# Module-level functions matching dispatch and PROJECT.md requirements
def inject_code(page: Any, code: str) -> bool:
    """
    Inject source code into Ace Editor on Guvi CodeKata workspace.
    Fulfills dispatch mission signature: inject_code(page: Any, code: str) -> bool
    """
    return _default_adapter.inject_code(page, code)


def get_editor_code(page: Any) -> str:
    """
    Read current code from Ace Editor buffer.
    Fulfills dispatch mission signature: get_editor_code(page: Any) -> str
    """
    return _default_adapter.get_code(page)


def wait_for_editor(page: Any, timeout: float = 10.0) -> bool:
    """
    Wait until Ace Editor is ready for interaction.
    Fulfills dispatch mission signature: wait_for_editor(page: Any, timeout: float = 10.0) -> bool
    """
    return _default_adapter.wait_for_ready(page, timeout)


# Canonical alias matching PROJECT.md §solver/ ↔ drivers/guvi_driver.py contract
inject_code_into_ace = inject_code
