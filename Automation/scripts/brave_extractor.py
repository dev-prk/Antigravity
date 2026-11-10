import subprocess
import json
import time
import os
import base64

def eval_js_on_url(url: str, js_code: str, wait_secs: float = 6.0) -> str:
    # Wrap js_code in an IIFE that returns a string
    wrapped_js = f"""
    (() => {{
        try {{
            const val = (function() {{ {js_code} }})();
            return val !== undefined ? String(val) : "";
        }} catch(e) {{
            return "ERROR: " + e.toString();
        }}
    }})();
    """
    b64 = base64.b64encode(wrapped_js.encode("utf-8")).decode("ascii")
    js_init = f"window.eval(decodeURIComponent(escape(atob('{b64}'))))"

    # Reuse existing Brave session: create tab in window 1, navigate, extract, close tab
    applescript_code = f'''
tell application "Brave Browser"
    set w to window 1
    set t to make new tab at end of tabs of w with properties {{URL:"{url}"}}
    delay {wait_secs}
    set res to execute t javascript "{js_init}"
    close t
    return res
end tell
'''
    res = subprocess.run(["osascript", "-e", applescript_code], capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"AppleScript error: {res.stderr}")
    return res.stdout.strip()




