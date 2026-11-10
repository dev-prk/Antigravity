"""Headless: apply difficulty filter, capture XHR, count pages."""
import sys, os, re, time, json
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "data", "storage_state.json")
diff = sys.argv[1] if len(sys.argv) > 1 else "Medium"

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(storage_state=STATE, viewport={"width": 1400, "height": 900})
    pg = ctx.new_page()
    reqs = []
    pg.on("response", lambda r: reqs.append((r.request.method, r.url, r.headers.get("content-type", ""))) if r.request.resource_type in ("xhr", "fetch") else None)
    pg.goto("https://www.guvi.in/code-kata/", wait_until="domcontentloaded", timeout=60000)
    time.sleep(4)
    reqs.clear()
    pg.click("#difficulty-filter-id")
    time.sleep(0.5)
    pg.click(f"li.difficulty-filter-option:has-text('{diff}')")
    time.sleep(3)
    print("URL", pg.url)
    for m, u, ct in reqs:
        print("REQ", m, u[:200], ct)
    nums = [b_.inner_text().strip() for b_ in pg.query_selector_all("button.page-no")]
    print("PAGES", nums)
    rows = pg.query_selector_all("tbody tr")
    print("ROWS", len(rows))
    for r in rows[:5]:
        print("ROW:", r.inner_text().replace("\n", " | ")[:200])
    b.close()
