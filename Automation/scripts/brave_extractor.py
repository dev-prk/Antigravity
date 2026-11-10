import subprocess
import json
import time
import os

def eval_js_on_url(url: str, js_code: str, wait_secs: float = 6.0) -> str:
    # Save js to a temp file or encode it
    # Even simpler: base64 encode the JS, and in AppleScript decode or in JS use eval(atob(...))
    import base64
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    js_wrapped = f"window.eval(decodeURIComponent(escape(atob('{b64}'))))"
    # In AppleScript, double quotes need to be escaped
    applescript_code = f'''
tell application "Brave Browser"
    set w to make new window
    tell active tab of w
        set URL to "{url}"
    end tell
    delay {wait_secs}
    set res to execute active tab of w javascript "{js_wrapped}"
    close w
    return res
end tell
'''
    res = subprocess.run(["osascript", "-e", applescript_code], capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"AppleScript error: {res.stderr}")
    return res.stdout.strip()

if __name__ == "__main__":
    test_js = "JSON.stringify({url: window.location.href, title: document.title})"
    res = eval_js_on_url("https://talent500.com/jobs/", test_js, wait_secs=5)
    print("Result:", res)

