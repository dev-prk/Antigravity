# GUVI Autopilot — Deliver Brief & Progress Tracker

## Brief
1. **Ask:** Bring GUVI CodeKata Solved to 100% using Python for all code questions, and also complete SQLKata (using SQL), WebKata (using HTML/CSS/JS), and FixTheCode (using Python) in the single foreground Brave Browser tab.
2. **Must-haves:** "i want solved to be 100%", "next we also have sqlkata, webkata and fix the code", "Use python to solve all the code question and obviously we use sql for sqlkata and relevant things for webkata", plus active constraints: foreground Brave Browser (`/Applications/Brave Browser.app`), strictly 1 single tab, fast cadence, `$0` `FreeLLMAPI` worker synthesis first.
3. **Done test:** Live GUVI dashboards on `guvi.in/code-kata/`, `guvi.in/sqlkata/`, `guvi.in/webkata/`, and `guvi.in/debugging/` are inspected and screenshotted in foreground Brave showing verified completion across every solvable item, with saved solutions on disk.
4. **Expert gap:**
   - ~5% of CodeKata / FixTheCode problems are college-lab locked to `C`/`C++`/`Java` in `<select id="editorModeSelectDesktop">` (no `PYTHON 3` option exists). We must ALWAYS select `PYTHON 3` (or `PYTHON 2`) whenever Python is in the dropdown, and only use the locked language when GUVI omits Python from the dropdown so `100%` Solved is achievable.
   - SQLKata problems are multi-subquestion scenarios (`Question 1`, `Question 2`, `Question 3`, `Question 4` inside one problem!) with database schema tabs (`Schema` / `Tables`) that must each be answered and submitted for the parent problem to become `Solved!`.
   - WebKata problems have separate `HTML`, `CSS`, and `JS` editor tabs and client-side DOM/style assertions.
   - ~66 CodeKata slugs were missed by naive title-slugification; we must discover the exact live remaining unsolved rows (`Yet to start` + `In progress`) directly from GUVI's catalog API / `q-data.json` / table click-through.
5. **Smallest version:** One clean, resumable single-tab Brave runner + `$0` `FreeLLMAPI` pre-solver covering (a) remaining unsolved CodeKata problems (`PYTHON 3` first, multi-pass repair on `Wrong Answer`), (b) SQLKata multi-subquestion SQL solver, (c) FixTheCode Python debugger, and (d) WebKata HTML/CSS/JS solver.
6. **Not building:** Multi-tab/multi-window browsers, paid-API bulk loops, or automation for graded Zen Class exams (`Mod11`–`Mod15`, `CCT`).
7. **Unknowns:** Assume locked non-Python CodeKata problems (~5% where GUVI disables Python in the dropdown) should still be solved in their required language so overall CodeKata reaches as close to 100.00% as GUVI's judge permits, while 100% of Python-capable code questions use `PYTHON 3`.

---

## Completed Baseline
- **Zen Class Projects**: `7/7` submitted (`zenclass_guvi/screenshots/final_zenclass_submitted.png`).
- **CodeKata Baseline**: `1,150` verified in pipeline / `54.31%` (`~1,185` / `~2,182`) live on GUVI (`zenclass_guvi/screenshots/final_codekata_verified.png`).

## Active Next Steps
- [ ] Finish live DOM/API inspection of `SQLKata`, `WebKata`, `FixTheCode`, and exact remaining `CodeKata` unsolved list.
- [ ] Thin end-to-end slice: verify 1 live solve each on `SQLKata`, `FixTheCode` (Python), and `WebKata`, plus 1 previously failed `CodeKata` repair.
- [ ] Execute full single-tab foreground Brave completion across `SQLKata`, `FixTheCode`, `WebKata`, and remaining `CodeKata` (`Yet to start` + `In progress` -> `100%`).
- [ ] Verify live dashboards & screenshots across all 4 platforms.
