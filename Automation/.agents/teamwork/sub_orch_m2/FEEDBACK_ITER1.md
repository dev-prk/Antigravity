# Review & Challenger Feedback — Iteration 1

## Summary of Gate Verdicts
- Auditor 1: **CLEAN** (Zero integrity violations)
- Reviewer 1: **APPROVE** (Noted Knapsack weight-value swap defect)
- Reviewer 2: **REQUEST_CHANGES** (IndentationError on Attempt 2 LCS/Edit Distance, Stdin stream exhaustion, UnboundLocalError)
- Challenger 1: **DISCONFIRMED** (10 concrete algorithmic/I/O defects in Feature 5)
- Challenger 2: **DISCONFIRMED** (4 defects in Feature 6: Attempt 2 indentation, scoping, numeric CSS leak, escaped newline delimiter)

## Detailed Defect List & Fix Requirements

### 1. Knapsack Weight-Value Inversion Bug (`TEMPLATE_DP_01_KNAPSACK`)
- **Location**: `solver/code_generator.py:545-546`
- **Issue**: `if max(weights, default=0) > w_cap and max(values, default=0) <= w_cap: weights, values = values, weights`. When an item's weight exceeds capacity, it incorrectly swaps weights and values, outputting an invalid answer (e.g. 15 instead of 0).
- **Fix**: Remove this heuristic entirely or only swap if weights are definitely the values in known swapped formats, but never swap simply because an item exceeds capacity.

### 2. LCS & Edit Distance Single-Read & Indentation Fix (`TEMPLATE_DP_LCS` & `TEMPLATE_DP_EDIT_DISTANCE`)
- **Location**: Lines 616–625 and 642–651
- **Issues**:
  - Stream exhaustion on single-line inputs (`sys.stdin.read().splitlines()` consumes EOF, second `read().split()` returns empty list).
  - Nested 8-space indent `tokens = sys.stdin.read().split()` causes `IndentationError` and `UnboundLocalError` when Attempt 2 injects 4-space snippets (`regex_snippet` or `safe_bounds_snippet`).
- **Fix**: Use unified single-read template:
  ```python
  raw = sys.stdin.read().strip()
  if not raw:
      print(0)
      return
  lines = [line.strip() for line in raw.splitlines() if line.strip()]
  if len(lines) >= 2:
      s1, s2 = lines[0], lines[1]
  else:
      tokens = raw.split()
      if len(tokens) >= 2:
          s1, s2 = tokens[0], tokens[1]
      else:
          print(0)
          return
  ```

### 3. Coin Change Partitioning (`TEMPLATE_DP_COIN_CHANGE`)
- **Location**: Lines 568–576
- **Issue**: First denomination `1` satisfies `len(nums) >= nums[0] + 2`, misidentifying `1` as count $N$ and `2` as target on `"1 2 5\n11"`.
- **Fix**: Reliably partition denominations and target (e.g. if last number is significantly different or checking standard CodeKata patterns where target is last).

### 4. Topological Sort Zero-Base Bug (`TEMPLATE_GRAPH_TOPOLOGICAL_SORT`)
- **Location**: Lines 780–785
- **Issue**: When 1-indexed graph has an isolated vertex $V$, `max_node` in edges $< V$ causes `base = 0`, hallucinating vertex 0 and omitting vertex $V$.
- **Fix**: Check `min_node == 0` or if any edge contains 0 to set `base = 0`, else `base = 1`.

### 5. Balanced Brackets Space Truncation (`TEMPLATE_STRING_BALANCED_BRACKETS`)
- **Location**: Line 995
- **Issue**: `raw.split()[0]` evaluates to `'('` on `"( [ ] )"`, dropping subsequent tokens.
- **Fix**: Filter bracket characters directly: `s = ''.join(c for c in raw if c in '()[]{}')`.

### 6. Semantic Router Substring Collision (`"lis"` in `"list"`)
- **Location**: Line 1234
- **Issue**: `"lis" in full_text` matches English word `"list"` (e.g. "Reverse Linked List" routed to LIS DP).
- **Fix**: Use regex word boundary `re.search(r"\blis\b", full_text)`.

### 7. Matrix Rotation Rectangular Handling (`TEMPLATE_MATRIX_ROTATE_90`)
- **Location**: Lines 1084–1086
- **Issue**: Assumes square matrix `n = int(len(nums) ** 0.5)`, truncating rectangular matrices.
- **Fix**: Check if first two numbers represent $R, C$ dimensions when $R \times C == len(nums) - 2$.

### 8. Island Count Binary String Grid (`TEMPLATE_GRAPH_ISLANDS_COUNT`)
- **Location**: Lines 807–813
- **Issue**: Unspaced binary rows `"110"` are parsed as integer `110`.
- **Fix**: Parse lines and unpack digits if tokens don't match $R \times C$.

### 9. BFS Shortest Path 0-Indexed Node Default (`TEMPLATE_GRAPH_BFS_SHORTEST_PATH`)
- **Location**: Lines 711–712
- **Issue**: Defaults `start=1, end=v` even on 0-indexed graphs.
- **Fix**: Respect graph base (`base = 0 if any 0 in edges else 1`).

### 10. Attempt 2 CSS Numeric Leak & Delimiter Adaptation
- **Location**: `_refine_solution`
- **Issue**:
  - `re.findall(r'-?\d+', ' '.join(tokens))` extracts numbers from CSS styles like `width: 100px`.
  - Delimiter matching only checks literal `\n`, missing escaped `\\n`.
- **Fix**:
  - Strip CSS blocks `re.sub(r'\{[^}]*\}', '', text)` before extracting numbers.
  - Check both `"\n" in exp_val` and `"\\n" in exp_val`.
