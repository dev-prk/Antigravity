"""Headless probe of Guvi CodeKata catalog: pagination + difficulty filter controls."""
import sys, os, re, time, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from playwright.sync_api import sync_playwright

STATE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "storage_state.json")

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(storage_state=STATE if os.path.exists(STATE) else None, viewport={"width": 1400, "height": 900})
    pg = ctx.new_page()
    pg.goto("https://www.guvi.in/code-kata/", wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    print("URL", pg.url)
    print("LOGIN BTN visible:", pg.locator("text=Login").first.is_visible() if pg.locator("text=Login").count() else False)
    rows = pg.query_selector_all("tbody tr")
    print("ROWS", len(rows))
    for r in rows[:3]:
        print("ROW:", r.inner_text().replace("\n", " | ")[:200])
    # pagination / filter candidates
    btns = pg.query_selector_all("button")
    for bt in btns:
        t = (bt.inner_text() or "").strip().replace("\n", " ")
        al = bt.get_attribute("aria-label") or ""
        if t or al:
            print("BTN:", repr(t[:40]), "aria:", al[:40], "cls:", (bt.get_attribute("class") or "")[:60])
    for s in pg.query_selector_all("select"):
        print("SELECT:", s.get_attribute("id"), s.inner_text()[:200].replace("\n", ","))
    html = pg.content()
    for kw in ["Medium", "Hard", "difficulty", "page="]:
        idxs = [m.start() for m in re.finditer(kw, html)][:3]
        for i in idxs:
            print(f"CTX[{kw}]:", html[max(0, i-150):i+150].replace("\n", " "))
    b.close()
