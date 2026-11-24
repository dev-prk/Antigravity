# Exam 01: fix parallel plans (rejection flow)

You delivered the EXPLAIN analyzer in ~/Documents/Antigravity/SkillTest. The reviewer rejected it:

> On parallel plans the self times are wrong. In `parallel_plan.txt` (this folder) the orders
> Parallel Seq Scan shows 1800 ms self time; the real wall-clock self time is 600 ms. The
> percentages add up to more than 100%.

Follow `/deliver`, section 8 (When the user rejects the work).

- Find the cause, not just this symptom. Any plan shape with parallel workers must be right.
- Done test: `python3 ~/Documents/Antigravity/exams/01_parallel_selftime/check.py ~/Documents/Antigravity/SkillTest`
  prints `RESULT: PASS`. Do not edit check.py or parallel_plan.txt.
- The reviewer will also run plan shapes you have not seen.
- Change only what the fix needs. No new features.
- In PROGRESS.md, write one evidence line per claim (claim → command → what you saw), with one
  node's self time worked out by hand.
- End with the section 7 report. Under "Not checked", list the parallel shapes you did not try.
