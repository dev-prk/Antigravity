# Verification Standards & Evidence Governance

## 1. Verifier Separation Principle
1. **Generator Never Grades Own Homework**:
   - The implementing agent cannot serve as the final verification authority for its own work.
   - Independent automated test suites, independent verifier modules, or a forensic auditor must validate task outputs against objective criteria.

## 2. Evidentiary Standards
1. **Concrete Evidence Recording**:
   - Every claim of completion or fact assertion must be backed by an entry in the SQLite `evidence` table.
   - Evidence records must capture:
     - `command`: exact shell command or test invocation.
     - `exit_code`: process return code (0 for pass).
     - `stdout`: captured standard output (secrets redacted).
     - `stderr`: captured standard error (secrets redacted).
     - `content_hash`: SHA-256 hash of verified artifact.

2. **Test Automation**:
   - All tests in `tests/` must be automated and executable via `python3 -m pytest tests/ -v`.
   - Flaky, dummy, or mocked tests asserting hardcoded expected strings without genuine logic are strictly prohibited.
   - Resumption tests must verify that an interrupted task restarts from `HANDOFF.md` and database state without re-executing completed steps.
