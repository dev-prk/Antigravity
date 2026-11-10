"""
ck_scrape.py - Headless (background) scraper for Guvi CodeKata Medium/Hard problems.

Phase A: crawl the filtered catalog (Medium, Hard) -> data/ck_catalog.json
Phase B: visit each pending problem and dump its statement + sample cases
         -> data/ck_problems/<slug>.json   (resume-safe: skips existing files)

Zero LLM cost. Never opens a visible window.
"""
import sys, os, re, time, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from playwright.sync_api import sync_playwright
from solver.extractor import extract_problem_spec

STATE = os.path.join(ROOT, "data", "storage_state.json")
CATALOG = os.path.join(ROOT, "data", "ck_catalog.json")
PROB_DIR = os.path.join(ROOT, "data", "ck_problems")
os.makedirs(PROB_DIR, exist_ok=True)


def slugify(title):
    t = re.sub(r"^\d+\.\s*", "", title)
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def crawl(pg, diff):
    pg.goto("https://www.guvi.in/code-kata/", wait_until="domcontentloaded", timeout=60000)
    time.sleep(4)
    try:
        pg.select_option("select#itemsPerPage", index=2)  # 50 per page
        time.sleep(2)
    except Exception as e:
        print("itemsPerPage note:", e)
    pg.click("#difficulty-filter-id")
    time.sleep(0.5)
    pg.click(f"li.difficulty-filter-option:has-text('{diff}')")
    time.sleep(3)
    out, seen_first = [], set()
    for page_no in range(1, 200):
        rows = pg.query_selector_all("tbody tr")
        first = rows[0].inner_text() if rows else ""
        if first in seen_first:
            break
        seen_first.add(first)
        for r in rows:
            tds = r.query_selector_all("td")
            if len(tds) < 4:
                continue
            html0 = tds[0].inner_html() or ""
            done = "#completed-icon_svg__a" in html0 or "#0DBA4B" in html0
            cells = [c.inner_text().strip() for c in tds]
            title = next((c for c in cells if re.match(r"^\d+\.\s", c)), cells[0])
            d = next((c for c in cells if c in ("Easy", "Medium", "Hard")), diff)
            out.append({"title": title, "slug": slugify(title), "difficulty": d, "completed": done})
        print(f"[{diff}] page {page_no}: total {len(out)}", flush=True)
        nxt = pg.query_selector('button[aria-label="Go to next page"]')
        if not nxt or nxt.get_attribute("disabled") is not None:
            break
        nxt.click()
        time.sleep(1.5)
    return out


def main():
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(storage_state=STATE, viewport={"width": 1400, "height": 900})
        pg = ctx.new_page()
        if os.path.exists(CATALOG) and "--recrawl" not in sys.argv:
            catalog = json.load(open(CATALOG))
        else:
            catalog = []
            for diff in ("Medium", "Hard"):
                catalog += crawl(pg, diff)
            json.dump(catalog, open(CATALOG, "w"), indent=1)
        pending = [c for c in catalog if not c["completed"]]
        print(f"Catalog: {len(catalog)} medium/hard, {len(pending)} pending", flush=True)
        for i, c in enumerate(pending, 1):
            fp = os.path.join(PROB_DIR, c["slug"] + ".json")
            if os.path.exists(fp):
                continue
            try:
                pg.goto(f"https://www.guvi.in/code-kata/{c['slug']}/", wait_until="domcontentloaded", timeout=45000)
                time.sleep(2.5)
                spec = extract_problem_spec(pg)
                # Prefer raw visible problem pane text for fidelity
                raw = ""
                for sel in [".problem-description", "#problem-description", ".question-content", "main"]:
                    el = pg.query_selector(sel)
                    if el:
                        raw = el.inner_text()
                        if len(raw) > 80:
                            break
                data = {
                    **c,
                    "description": spec.description,
                    "input_spec": spec.input_spec,
                    "output_spec": spec.output_spec,
                    "constraints": spec.constraints,
                    "samples": [{"input": s.input_text, "output": s.expected_output} for s in spec.sample_cases],
                    "raw": raw[:4000],
                }
                json.dump(data, open(fp, "w"), indent=1, default=str)
                print(f"[{i}/{len(pending)}] saved {c['slug']}", flush=True)
            except Exception as e:
                print(f"[{i}/{len(pending)}] ERROR {c['slug']}: {e}", flush=True)
        try:
            ctx.storage_state(path=STATE)
        except Exception:
            pass
        b.close()


if __name__ == "__main__":
    main()
