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

    applescript_code = f'''
tell application "Brave Browser"
    set w to make new window
    tell active tab of w
        set URL to "{url}"
    end tell
    delay {wait_secs}
    set res to execute active tab of w javascript "{js_init}"
    close w
    return res
end tell
'''
    res = subprocess.run(["osascript", "-e", applescript_code], capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"AppleScript error: {res.stderr}")
    return res.stdout.strip()



