# Dead Ends — E2E Testing Track

| Iteration | Approach Tried | Why It Failed | Files Touched |
|-----------|---------------|---------------|---------------|
| 1 | Test helper `_safe_generate_solution` hardcoding code snippet for `ValueError`, vacuous mock-on-mock tests (`test_t2_r1_04`, `test_t2_r3_04`), bypassing `GuviDriver` and testing inlined regex and local dictionary loops | Flagged by Reviewer 1, Reviewer 2, Challenger 1, and Forensic Auditor as INTEGRITY VIOLATION and FAILS AUDIT. Test suite was blind to driver changes and code generator mutations. | `tests/e2e/test_medium_hard_codekata.py` |
