# Explorer R2-1 Investigation & Code Remediation Report: Milestone 2 Feature 5 Defects

- **Explorer**: Explorer R2-1 (`explorer`, read-only investigation)
- **Sub-Orchestrator Parent ID**: `17228c22-a76a-4e52-a4ec-28b3698ff179`
- **Milestone**: Milestone 2: Intelligent Solver & Error Adaptation (Iteration 2)
- **Target File**: `zenclass_guvi/solver/code_generator.py`
- **Scope**: Feature 5 Algorithmic and Parsing Defect Remediation
- **Handoff Type**: Hard (Investigation & Strategy Complete)

---

## 1. Observation

Direct inspection of `zenclass_guvi/solver/code_generator.py` and empirical execution via `solver.test_runner.test_solution()` against test cases from `tests/test_m2_code_generator.py` and `tests/test_m2_stress_challenger.py` reveals the following exact line-level defects across Feature 5 templates:

### Defect 1: `TEMPLATE_DP_01_KNAPSACK` Weight-Value Inversion
- **File & Lines**: `zenclass_guvi/solver/code_generator.py:545-546`
- **Verbatim Code**:
  ```python
  if max(weights, default=0) > w_cap and max(values, default=0) <= w_cap:
      weights, values = values, weights
  ```
- **Observed Behavior**:
  When an individual item's weight exceeds the knapsack capacity $W$ (`max(weights) > w_cap`), but its value happens to be $\le W$, the heuristic mistakenly assumes the input inverted weights and values.
  - Test Input: `SampleCase("1 10\n15\n5", "0")` (1 item, capacity 10, wt 15, val 5). The item cannot fit, expected output: `0`.
  - Actual Result: Swaps wt and val so wt=5, val=15. Output is `15`.
  - Multi-item Input: `SampleCase("2 10\n20 6\n8 4", "4")` (item 1 wt 20 val 8; item 2 wt 6 val 4). Expected: `4`. Actual Result: Swaps, outputting `20`.

### Defect 2: `TEMPLATE_DP_COIN_CHANGE` Denomination-Target Partitioning
- **File & Lines**: `zenclass_guvi/solver/code_generator.py:568-576`
- **Verbatim Code**:
  ```python
  if len(nums) >= nums[0] + 2:
      target = nums[1]
      coins = nums[2:2 + nums[0]]
  elif len(nums) == nums[0] + 1:
      target = nums[-1]
      coins = nums[1:-1]
  else:
      target = nums[-1]
      coins = nums[:-1]
  ```
- **Observed Behavior**:
  On inputs where coin denominations precede target without an initial count $N$ (e.g. `SampleCase("1 2 5\n11", "3")`), the first denomination is `nums[0] = 1`.
  `len(nums) >= nums[0] + 2` evaluates to `4 >= 3` (True).
  The code erroneously assigns `target = nums[1] = 2` and `coins = nums[2:3] = [5]`.
  Actual Result: Outputs `-1` instead of `3`.

### Defect 3: `TEMPLATE_GRAPH_TOPOLOGICAL_SORT` Zero-Base Misattribution & Queue Ordering
- **File & Lines**: `zenclass_guvi/solver/code_generator.py:780-786`
- **Verbatim Code**:
  ```python
  base = 1 if max_node == v else 0
  adj = defaultdict(list)
  in_degree = {i: 0 for i in range(base, base + v)}
  ...
  q = deque([node for node in in_degree if in_degree[node] == 0])
  ```
- **Observed Behavior**:
  1. In a 1-indexed DAG where an isolated vertex $V$ has no incident edges (e.g. `SampleCase("3 1\n1 2", "1 2 3")`), `max_node` is 2. Because `2 != 3`, `base` is set to 0. Vertices initialized are `{0, 1, 2}`. Vertex 0 is invented, and isolated vertex 3 is omitted, printing `"0 1 2"`.
  2. Even when `base = 1` is correctly set, using an un-ordered `collections.deque` causes ties among multiple degree-0 nodes to be resolved in insertion order rather than deterministic lexicographical order, producing `"1 3 2"` instead of `"1 2 3"`.

### Defect 4: `TEMPLATE_GRAPH_BFS_SHORTEST_PATH` 0-Indexed Node Defaulting
- **File & Lines**: `zenclass_guvi/solver/code_generator.py:711-712`
- **Verbatim Code**:
  ```python
  start = nums[idx] if idx < len(nums) else 1
  end = nums[idx + 1] if idx + 1 < len(nums) else v
  ```
- **Observed Behavior**:
  When no explicit source/target query tokens follow the edge list (e.g. `SampleCase("3 2\n0 1\n1 2", "2")` with $V=3, E=2$), the template hardcodes `start = 1` and `end = 3`.
  In a 0-indexed graph (vertices $\{0, 1, 2\}$), vertex 3 does not exist.
  Actual Result: Returns `-1` instead of `2`.
  *(Note: Identical vulnerability exists in `TEMPLATE_GRAPH_DIJKSTRA:745-746`)*.

### Defect 5: `TEMPLATE_STRING_BALANCED_BRACKETS` Space-Token Truncation
- **File & Lines**: `zenclass_guvi/solver/code_generator.py:995`
- **Verbatim Code**:
  ```python
  s = raw.split()[0] if raw.split() else ''
  ```
- **Observed Behavior**:
  On space-separated bracket expressions (e.g. `SampleCase("( [ ] )", "yes")`), `raw.split()[0]` evaluates to `'('`, discarding all subsequent tokens `'['`, `']'`, `')'`.
  Actual Result: Stack retains `'('`, outputting `'no'` instead of `'yes'`.

### Defect 6: `TEMPLATE_MATRIX_ROTATE_90` Rectangular Truncation
- **File & Lines**: `zenclass_guvi/solver/code_generator.py:1080-1086`
- **Verbatim Code**:
  ```python
  n = nums[0]
  if len(nums) == n * n + 1:
      elements = nums[1:]
  else:
      n = int(len(nums) ** 0.5)
      elements = nums[:n * n]
  matrix = [elements[i * n:(i + 1) * n] for i in range(n)]
  ```
- **Observed Behavior**:
  The template assumes the matrix is strictly square $N \times N$.
  On rectangular matrices (e.g. `SampleCase("2 3\n1 2 3\n4 5 6", "4 1\n5 2\n6 3")` with $R=2, C=3$), `len(nums) = 8`.
  The code computes `n = int(8 ** 0.5) = 2`, slicing `elements = nums[:4] = [2, 3, 1, 2]`.
  Actual Result: Discards trailing elements and outputs corrupted $2 \times 2$ grid `'1 2\n2 3'`.

### Defect 7: `TEMPLATE_GRAPH_ISLANDS_COUNT` Unspaced Binary Row Parsing
- **File & Lines**: `zenclass_guvi/solver/code_generator.py:807-813`
- **Verbatim Code**:
  ```python
  tokens = sys.stdin.read().split()
  if not tokens: return
  nums = [int(x) for x in tokens]
  if len(nums) < 2: return
  r, c = nums[0], nums[1]
  grid_vals = nums[2:2 + r * c]
  if len(grid_vals) < r * c:
      print(0)
      return
  ```
- **Observed Behavior**:
  On inputs where rows are binary strings without whitespace (e.g. `SampleCase("3 3\n110\n010\n001", "1")`), `tokens` contains `['3', '3', '110', '010', '001']`.
  `nums` parses `'110'` as single integer `110`. `len(grid_vals) = 3 < 9`, which immediately aborts with `print(0)`.
  Actual Result: Outputs `0` instead of counting components.

---

## 2. Logic Chain

1. **Premise**: Competitive programming platforms (Guvi CodeKata) supply inputs in diverse formats: single-line vs multi-line, 0-indexed vs 1-indexed, space-separated vs continuous strings, and optional dimension headers.
2. **Knapsack Invariant (Defect 1)**:
   In 0/1 Knapsack, an item with weight $w_i > W$ simply cannot be chosen; this is an expected physical condition, not proof that weights and values are swapped. Removing lines 545–546 restores the standard knapsack invariant without breaking any valid problem instances.
3. **Coin Change Invariant (Defect 2)**:
   Line breaks provide strong structural signals:
   - If the last line contains exactly 1 integer, it is always the target amount $T$, and preceding lines contain coin denominations $C$ (or $N$ followed by $C$).
   - If the first line contains 2 integers $(N, T)$, one equals the count of remaining tokens, disambiguating $N$ from $T$.
   - Single-line fallback checks strict equality `nums[0] == len(nums) - 2` rather than weak `>=`.
4. **Topological Sort Invariant (Defect 3)**:
   In graph theory, a graph is 0-indexed if and only if 0 appears as a vertex label in the edge list (`any(u == 0 or w == 0 for u, w in edges)`). If 0 is absent and all edge nodes are $\ge 1$, the graph is 1-indexed (`base = 1`), regardless of whether `max_node == v`. Furthermore, Kahn's algorithm must use `heapq` (a min-heap) to guarantee lexicographical tie-breaking for deterministic output matching platform test cases.
5. **BFS Shortest Path Invariant (Defect 4)**:
   When no explicit query endpoints are provided, the default span of a graph is `base` to `base + v - 1`. For 0-indexed graphs, this is $0 \to V-1$. For 1-indexed graphs, this is $1 \to V$. Setting defaults dynamically based on vertex presence guarantees valid graph queries.
6. **String Brackets Invariant (Defect 5)**:
   Tokens in bracket expressions may be separated by whitespace or embedded in algebraic expressions. Extracting all bracket characters via `''.join(c for c in raw if c in '()[]{}')` completely removes whitespace and non-bracket tokens while preserving matching order.
7. **Matrix Rotation Invariant (Defect 6)**:
   A matrix of dimensions $R \times C$ satisfies `len(nums) == nums[0] * nums[1] + 2` when $R, C$ are supplied as leading tokens. Clockwise 90-degree rotation maps an $R \times C$ matrix to a $C \times R$ matrix: `rotated = [list(row) for row in zip(*matrix)][::-1]` reversed along rows.
8. **Island Grid Invariant (Defect 7)**:
   Binary grids are often supplied as strings of digits without spaces (e.g. `'110'`). If token count $< R \times C$, extracting individual characters `[int(ch) for t in rem_tokens for ch in t if ch in '01']` cleanly recovers all $R \times C$ cells.

---

## 3. Caveats

1. **Islands Count: 4-Directional vs 8-Directional Connectivity**:
   - In `tests/test_m2_code_generator.py:301`, `SampleCase("3 3\n1 1 0 0 0 1 1 0 1", "3")` mandates **4-directional connectivity** (orthogonal neighbors only: up, down, left, right). Under 8-directional connectivity, that test would evaluate to `2` and fail.
   - In `tests/test_m2_stress_challenger.py:240`, `SampleCase("3 3\n110\n010\n001", "1")` assumed 8-directional connectivity (or a typo where (1,1) connects diagonally to (2,2)). Under 4-directional connectivity, `110 / 010 / 001` has **2** islands: `{(0,0), (0,1), (1,1)}` and `{(2,2)}`.
   - **Recommendation**: Keep `TEMPLATE_GRAPH_ISLANDS_COUNT` strictly **4-directional** to satisfy the core test suite. In `test_m2_stress_challenger.py`, either update the test grid to `"3 3\n110\n011\n001"` (which is 1 island in 4-way) or update the expected output to `"2"`.
2. **Topological Sort Min-Heap Requirement**:
   Merely fixing `base` is necessary but not sufficient. When multiple vertices have in-degree 0 (e.g., node 1 and isolated node 3), standard `deque` pops in insertion order (`1 3 2`), whereas competitive programming platforms (and Challenger 1) require lexicographical order (`1 2 3`). Using `heapq` is mandatory.
3. **Attempt 3 Sample Anchors**:
   On Attempt 3, `_refine_solution` wraps code in exact string matching against `SAMPLE_ANCHORS`. This masks algorithmic flaws on visible sample cases, but private hidden test cases fail without these line-level fixes.
4. **Co-located Defects**:
   - `TEMPLATE_GRAPH_DIJKSTRA` has the same 0-indexed endpoint defect as BFS and should receive the same base-aware start/end defaulting.
   - `TEMPLATE_DP_LCS` and `TEMPLATE_DP_EDIT_DISTANCE` have the double `sys.stdin.read()` stream exhaustion defect and should be updated to a single `raw = sys.stdin.read().strip()` read.
   - `_match_domain_template` line 1234 has `"lis" in full_text` which matches the word `"list"`, and should be updated to regex `bool(re.search(r"\blis\b", full_text))`.

---

## 4. Conclusion & Concrete Code Remediation Recommendations

All 7 algorithmic and parsing defects have been thoroughly isolated, analyzed, and empirically validated using isolated dry-runs with `solver.test_runner.test_solution()`.

Below are the exact, line-level code replacement strategies for the implementer:

### Remediation 1: `TEMPLATE_DP_01_KNAPSACK`
- **File**: `zenclass_guvi/solver/code_generator.py`
- **Lines to Remove**: Lines 545–546
- **Diff**:
  ```diff
  --- a/zenclass_guvi/solver/code_generator.py
  +++ b/zenclass_guvi/solver/code_generator.py
  @@ -544,2 +544,0 @@
  -    if max(weights, default=0) > w_cap and max(values, default=0) <= w_cap:
  -        weights, values = values, weights
  ```
- **Replacement Code Block for `TEMPLATE_DP_01_KNAPSACK` (Lines 521–556)**:
  ```python
  TEMPLATE_DP_01_KNAPSACK = (
      "import sys\n\n"
      "def solve():\n"
      "    tokens = sys.stdin.read().split()\n"
      "    if not tokens: return\n"
      "    nums = [int(x) for x in tokens]\n"
      "    if len(nums) < 3:\n"
      "        print(0)\n"
      "        return\n"
      "    n, w_cap = nums[0], nums[1]\n"
      "    if len(nums) >= 2 + 2 * n:\n"
      "        weights = nums[2:2 + n]\n"
      "        values = nums[2 + n:2 + 2 * n]\n"
      "    elif (len(nums) - 2) % 2 == 0 and len(nums) > 2:\n"
      "        rem = nums[2:]\n"
      "        half = len(rem) // 2\n"
      "        weights = rem[:half]\n"
      "        values = rem[half:]\n"
      "    else:\n"
      "        w_cap = nums[-1]\n"
      "        rem = nums[:-1]\n"
      "        half = len(rem) // 2\n"
      "        weights = rem[:half]\n"
      "        values = rem[half:]\n"
      "    dp = [0] * (w_cap + 1)\n"
      "    for wt, val in zip(weights, values):\n"
      "        if wt <= 0: continue\n"
      "        for w in range(w_cap, wt - 1, -1):\n"
      "            if dp[w - wt] + val > dp[w]:\n"
      "                dp[w] = dp[w - wt] + val\n"
      "    print(dp[w_cap])\n\n"
      "if __name__ == '__main__':\n"
      "    solve()\n"
  )
  ```

---

### Remediation 2: `TEMPLATE_DP_COIN_CHANGE`
- **File**: `zenclass_guvi/solver/code_generator.py`
- **Lines to Replace**: Lines 558–588
- **Replacement Code Block**:
  ```python
  TEMPLATE_DP_COIN_CHANGE = (
      "import sys\n\n"
      "def solve():\n"
      "    raw = sys.stdin.read().strip()\n"
      "    if not raw: return\n"
      "    lines = [line.strip() for line in raw.splitlines() if line.strip()]\n"
      "    if len(lines) >= 2:\n"
      "        l0 = [int(x) for x in lines[0].split()]\n"
      "        l_last = [int(x) for x in lines[-1].split()]\n"
      "        middle = [int(x) for l in lines[1:-1] for x in l.split()]\n"
      "        if len(l_last) == 1:\n"
      "            target = l_last[0]\n"
      "            rest = l0 + middle\n"
      "            coins = rest[1:] if (len(rest) > 1 and rest[0] == len(rest) - 1) else rest\n"
      "        else:\n"
      "            coins = l_last\n"
      "            prefix = l0 + middle\n"
      "            if len(prefix) == 2:\n"
      "                if prefix[0] == len(coins): target = prefix[1]\n"
      "                elif prefix[1] == len(coins): target = prefix[0]\n"
      "                else: target = max(prefix)\n"
      "            elif len(prefix) == 1:\n"
      "                target = prefix[0]\n"
      "            else:\n"
      "                target = prefix[-1]\n"
      "    else:\n"
      "        tokens = raw.split()\n"
      "        nums = [int(x) for x in tokens]\n"
      "        if len(nums) == 1:\n"
      "            print(0 if nums[0] == 0 else -1)\n"
      "            return\n"
      "        if len(nums) >= 3 and nums[0] == len(nums) - 2:\n"
      "            target = nums[1]\n"
      "            coins = nums[2:]\n"
      "        elif len(nums) > 1 and nums[0] == len(nums) - 1:\n"
      "            target = nums[-1]\n"
      "            coins = nums[1:-1]\n"
      "        else:\n"
      "            target = nums[-1]\n"
      "            coins = nums[:-1]\n"
      "    if target < 0:\n"
      "        print(-1)\n"
      "        return\n"
      "    dp = [float('inf')] * (target + 1)\n"
      "    dp[0] = 0\n"
      "    for c in coins:\n"
      "        if c <= 0: continue\n"
      "        for x in range(c, target + 1):\n"
      "            if dp[x - c] + 1 < dp[x]:\n"
      "                dp[x] = dp[x - c] + 1\n"
      "    ans = dp[target]\n"
      "    print(ans if ans != float('inf') else -1)\n\n"
      "if __name__ == '__main__':\n"
      "    solve()\n"
  )
  ```

---

### Remediation 3: `TEMPLATE_GRAPH_TOPOLOGICAL_SORT`
- **File**: `zenclass_guvi/solver/code_generator.py`
- **Lines to Replace**: Lines 762–801
- **Replacement Code Block**:
  ```python
  TEMPLATE_GRAPH_TOPOLOGICAL_SORT = (
      "import sys, heapq\n"
      "from collections import defaultdict\n\n"
      "def solve():\n"
      "    tokens = sys.stdin.read().split()\n"
      "    if not tokens: return\n"
      "    nums = [int(x) for x in tokens]\n"
      "    if len(nums) < 2: return\n"
      "    v, e = nums[0], nums[1]\n"
      "    idx = 2\n"
      "    edges = []\n"
      "    for _ in range(e):\n"
      "        if idx + 1 < len(nums):\n"
      "            u, w = nums[idx], nums[idx + 1]\n"
      "            edges.append((u, w))\n"
      "            idx += 2\n"
      "    base = 0 if any(u == 0 or w == 0 for u, w in edges) else 1\n"
      "    adj = defaultdict(list)\n"
      "    in_degree = {i: 0 for i in range(base, base + v)}\n"
      "    for u, w in edges:\n"
      "        adj[u].append(w)\n"
      "        in_degree[w] = in_degree.get(w, 0) + 1\n"
      "    pq = [node for node in in_degree if in_degree[node] == 0]\n"
      "    heapq.heapify(pq)\n"
      "    res = []\n"
      "    while pq:\n"
      "        curr = heapq.heappop(pq)\n"
      "        res.append(curr)\n"
      "        for nxt in adj[curr]:\n"
      "            in_degree[nxt] -= 1\n"
      "            if in_degree[nxt] == 0:\n"
      "                heapq.heappush(pq, nxt)\n"
      "    if len(res) == v:\n"
      "        print(' '.join(map(str, res)))\n"
      "    else:\n"
      "        print(-1)\n\n"
      "if __name__ == '__main__':\n"
      "    solve()\n"
  )
  ```

---

### Remediation 4: `TEMPLATE_GRAPH_BFS_SHORTEST_PATH`
- **File**: `zenclass_guvi/solver/code_generator.py`
- **Lines to Replace**: Lines 694–726
- **Replacement Code Block**:
  ```python
  TEMPLATE_GRAPH_BFS_SHORTEST_PATH = (
      "import sys\n"
      "from collections import deque, defaultdict\n\n"
      "def solve():\n"
      "    tokens = sys.stdin.read().split()\n"
      "    if not tokens: return\n"
      "    nums = [int(x) for x in tokens]\n"
      "    if len(nums) < 2: return\n"
      "    v, e = nums[0], nums[1]\n"
      "    idx = 2\n"
      "    adj = defaultdict(list)\n"
      "    nodes = set()\n"
      "    for _ in range(e):\n"
      "        if idx + 1 < len(nums):\n"
      "            u, w = nums[idx], nums[idx + 1]\n"
      "            adj[u].append(w)\n"
      "            adj[w].append(u)\n"
      "            nodes.add(u)\n"
      "            nodes.add(w)\n"
      "            idx += 2\n"
      "    base = 0 if 0 in nodes else 1\n"
      "    start = nums[idx] if idx < len(nums) else base\n"
      "    end = nums[idx + 1] if idx + 1 < len(nums) else (base + v - 1)\n"
      "    dist = {start: 0}\n"
      "    q = deque([start])\n"
      "    while q:\n"
      "        curr = q.popleft()\n"
      "        if curr == end:\n"
      "            break\n"
      "        for nxt in adj[curr]:\n"
      "            if nxt not in dist:\n"
      "                dist[nxt] = dist[curr] + 1\n"
      "                q.append(nxt)\n"
      "    print(dist.get(end, -1))\n\n"
      "if __name__ == '__main__':\n"
      "    solve()\n"
  )
  ```

---

### Remediation 5: `TEMPLATE_STRING_BALANCED_BRACKETS`
- **File**: `zenclass_guvi/solver/code_generator.py`
- **Lines to Replace**: Lines 988–1009
- **Replacement Code Block**:
  ```python
  TEMPLATE_STRING_BALANCED_BRACKETS = (
      "import sys\n\n"
      "def solve():\n"
      "    raw = sys.stdin.read().strip()\n"
      "    if not raw:\n"
      "        print('yes')\n"
      "        return\n"
      "    s = ''.join(c for c in raw if c in '()[]{}')\n"
      "    mapping = {')': '(', ']': '[', '}': '{'}\n"
      "    stack = []\n"
      "    for ch in s:\n"
      "        if ch in mapping.values():\n"
      "            stack.append(ch)\n"
      "        elif ch in mapping:\n"
      "            if not stack or stack[-1] != mapping[ch]:\n"
      "                print('no')\n"
      "                return\n"
      "            stack.pop()\n"
      "    print('yes' if not stack else 'no')\n\n"
      "if __name__ == '__main__':\n"
      "    solve()\n"
  )
  ```

---

### Remediation 6: `TEMPLATE_MATRIX_ROTATE_90`
- **File**: `zenclass_guvi/solver/code_generator.py`
- **Lines to Replace**: Lines 1073–1094
- **Replacement Code Block**:
  ```python
  TEMPLATE_MATRIX_ROTATE_90 = (
      "import sys\n\n"
      "def solve():\n"
      "    raw = sys.stdin.read().strip()\n"
      "    if not raw: return\n"
      "    tokens = raw.split()\n"
      "    if len(tokens) < 2: return\n"
      "    nums = [int(x) for x in tokens]\n"
      "    if len(nums) >= 2 and nums[0] > 0 and nums[1] > 0 and len(nums) == nums[0] * nums[1] + 2:\n"
      "        r, c = nums[0], nums[1]\n"
      "        elements = nums[2:]\n"
      "    elif nums[0] > 0 and len(nums) == nums[0] * nums[0] + 1:\n"
      "        r = c = nums[0]\n"
      "        elements = nums[1:]\n"
      "    else:\n"
      "        lines = [l.strip() for l in raw.splitlines() if l.strip()]\n"
      "        line_lens = [len(l.split()) for l in lines]\n"
      "        if len(lines) > 1 and len(set(line_lens)) == 1:\n"
      "            r = len(lines)\n"
      "            c = line_lens[0]\n"
      "            elements = nums\n"
      "        else:\n"
      "            n = int(len(nums) ** 0.5)\n"
      "            r = c = n\n"
      "            elements = nums[:n * n]\n"
      "    if r <= 0 or c <= 0: return\n"
      "    matrix = [elements[i * c:(i + 1) * c] for i in range(r)]\n"
      "    rotated = [list(row) for row in zip(*matrix)]\n"
      "    for row in rotated:\n"
      "        row.reverse()\n"
      "    for row in rotated:\n"
      "        print(' '.join(map(str, row)))\n\n"
      "if __name__ == '__main__':\n"
      "    solve()\n"
  )
  ```

---

### Remediation 7: `TEMPLATE_GRAPH_ISLANDS_COUNT`
- **File**: `zenclass_guvi/solver/code_generator.py`
- **Lines to Replace**: Lines 803–835
- **Replacement Code Block**:
  ```python
  TEMPLATE_GRAPH_ISLANDS_COUNT = (
      "import sys\n"
      "from collections import deque\n\n"
      "def solve():\n"
      "    raw = sys.stdin.read().strip()\n"
      "    if not raw: return\n"
      "    tokens = raw.split()\n"
      "    if not tokens: return\n"
      "    if len(tokens[0]) > 1 and all(ch in '01' for ch in tokens[0]):\n"
      "        r = len(tokens)\n"
      "        c = len(tokens[0])\n"
      "        rem_tokens = tokens\n"
      "    else:\n"
      "        if len(tokens) < 2: return\n"
      "        try:\n"
      "            r, c = int(tokens[0]), int(tokens[1])\n"
      "            rem_tokens = tokens[2:]\n"
      "        except (ValueError, IndexError):\n"
      "            return\n"
      "    if len(rem_tokens) == r * c:\n"
      "        grid_vals = [int(x) for x in rem_tokens]\n"
      "    else:\n"
      "        digits = [int(ch) for t in rem_tokens for ch in t if ch in '01']\n"
      "        if len(digits) == r * c:\n"
      "            grid_vals = digits\n"
      "        elif len(rem_tokens) >= r * c:\n"
      "            grid_vals = [int(x) for x in rem_tokens[:r * c]]\n"
      "        else:\n"
      "            print(0)\n"
      "            return\n"
      "    grid = [grid_vals[i * c:(i + 1) * c] for i in range(r)]\n"
      "    visited = [[False] * c for _ in range(r)]\n"
      "    count = 0\n"
      "    for i in range(r):\n"
      "        for j in range(c):\n"
      "            if grid[i][j] == 1 and not visited[i][j]:\n"
      "                count += 1\n"
      "                q = deque([(i, j)])\n"
      "                visited[i][j] = True\n"
      "                while q:\n"
      "                    cr, cc = q.popleft()\n"
      "                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:\n"
      "                        nr, nc = cr + dr, cc + dc\n"
      "                        if 0 <= nr < r and 0 <= nc < c and grid[nr][nc] == 1 and not visited[nr][nc]:\n"
      "                            visited[nr][nc] = True\n"
      "                            q.append((nr, nc))\n"
      "    print(count)\n\n"
      "if __name__ == '__main__':\n"
      "    solve()\n"
  )
  ```

---

### Remediation 8: Supporting Defect Fixes (`LCS`, `Edit Distance`, `_match_domain_template`)
- **`TEMPLATE_DP_LCS` (Lines 616–625)**: Read `raw = sys.stdin.read().strip()` once; split `lines` or fallback to `raw.split()`.
- **`TEMPLATE_DP_EDIT_DISTANCE` (Lines 642–651)**: Same unified single-read fix as LCS.
- **`_match_domain_template` (Line 1234)**:
  ```python
  elif "longest increasing subsequence" in full_text or bool(re.search(r"\blis\b", full_text)) or ("increasing" in full_text and "subsequence" in full_text):
  ```
- **`TEMPLATE_GRAPH_DIJKSTRA` (Lines 745–746)**: Set `base = 0 if 0 in nodes else 1`, `start = nums[idx] if idx < len(nums) else base`, `end = nums[idx + 1] if idx + 1 < len(nums) else (base + v - 1)`.

---

## 5. Verification Method

To independently verify all proposed remediations before and after applying changes to `zenclass_guvi/solver/code_generator.py`:

### Command 1: Run Existing Unit Test Suite
```bash
cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi
python3 -m pytest tests/test_m2_code_generator.py -v
```
*Expected: 38 passing tests, 0 failures.*

### Command 2: Run Iteration 1 Challenger Suite
```bash
cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi
python3 -m pytest tests/test_m2_stress_challenger.py -v
```

### Invalidation Conditions:
1. If Knapsack outputs non-zero value on `SampleCase("1 10\n15\n5", "0")`, weights/values swap was not removed.
2. If Coin Change outputs `-1` on `SampleCase("1 2 5\n11", "3")`, denomination-first partitioning failed.
3. If Topo Sort outputs `0 1 2` on `SampleCase("3 1\n1 2", "1 2 3")`, base detection is still using `max_node == v`.
4. If BFS outputs `-1` on `SampleCase("3 2\n0 1\n1 2", "2")`, default endpoint logic still assumes 1-based indexing.
5. If Islands Count outputs `0` on `SampleCase("3 3\n110\n011\n001", "1")`, unspaced binary unpacking failed.
