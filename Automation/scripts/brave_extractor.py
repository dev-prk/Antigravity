import subprocess
import json
import time
import os
import base64

def eval_js_on_url(url: str, js_code: str, wait_secs: float = 6.0) -> str:
    # Wrap js_code so if it returns a Promise or value, it handles it
    wrapped_js = f"""
    (() => {{
        window.__extraction_done = false;
        window.__extraction_result = null;
        window.__extraction_error = null;
        try {{
            const res = (function() {{ {js_code} }})();
            if (res && typeof res.then === 'function') {{
                res.then(val => {{
                    window.__extraction_result = val;
                    window.__extraction_done = true;
                }}).catch(err => {{
                    window.__extraction_error = err ? err.toString() : 'Error in promise';
                    window.__extraction_done = true;
                }});
            }} else {{
                window.__extraction_result = res;
                window.__extraction_done = true;
            }}
        }} catch(e) {{
            window.__extraction_error = e ? e.toString() : 'Error executing script';
            window.__extraction_done = true;
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
    execute active tab of w javascript "{js_init}"
    set waited to 0
    repeat while waited < 15
        delay 0.5
        set waited to waited + 0.5
        set chk to (execute active tab of w javascript "window.__extraction_done ? 'DONE' : 'WAIT'")
        if chk is "DONE" then
            exit repeat
        end if
    end repeat
    set resVal to execute active tab of w javascript "window.__extraction_result"
    set resErr to execute active tab of w javascript "window.__extraction_error"
    close w
    if resErr is not missing value and resErr is not "" and resErr is not "null" then
        return "ERROR: " & resErr
    else
        return resVal
    end if
end tell

'''
    res = subprocess.run(["osascript", "-e", applescript_code], capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"AppleScript error: {res.stderr}")
    return res.stdout.strip()


