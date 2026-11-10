# Milestone 2 Exploration Report: Solver Architecture, Model Integration & Medium/Hard Algorithmic Synthesis

- **Date**: 2026-11-10T22:34:00Z
- **Author**: Explorer 1 (`teamwork_explorer`)
- **Conversation ID**: `2c309647-8167-4030-84cb-26c4c170c9d5`
- **Sub-Orchestrator Parent ID**: `17228c22-a76a-4e52-a4ec-28b3698ff179`
- **Milestone**: Milestone 2 — Intelligent Solver & Error Adaptation
- **Working Directory**: `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi`
- **State Folder**: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/sub_orch_m2/explorer_1`
- **Handoff Type**: Hard (Self-Contained Investigation Complete)

---

## 1. Observation

### 1.1 Existing Codebase & File Layout
Direct inspection of `solver/code_generator.py` (659 lines) and related solver infrastructure revealed the following exact components:

1. **`solver/code_generator.py` Data Model & Signatures**:
   - Lines 25–32:
     ```python
     @dataclass
     class GeneratedSolution:
         """Represents a synthesized algorithmic code solution with metadata."""
         code: str
         category: str
         confidence: float
         explanation: str
     ```
   - Lines 577–582:
     ```python
     def generate_solution(problem: Union[ProblemSpecification, Any]) -> GeneratedSolution:
         """
         Synthesizes an optimal Python 3 solution for a given problem specification.
         Returns GeneratedSolution containing verified code, category, confidence, and explanation.
         """
     ```
   - Lines 646–659:
     ```python
     def synthesize_solution(problem: Union[ProblemSpecification, Any]) -> str:
         """
         Contract wrapper returning the generated Python 3 source string.
         Fully compatible with PROJECT.md and E2E test harness.
         Validates AST syntax before returning.
         """
         solution = generate_solution(problem)
         try:
             ast.parse(solution.code)
         except SyntaxError:
             logger.error("Synthesized code failed AST validation, using fallback.")
             return TEMPLATE_FALLBACK_ECHO
         return solution.code
     ```

2. **Existing Canonical Catalog & Template Library**:
   - Lines 38–371 define `CANONICAL_SOLVERS: Dict[str, Dict[str, str]]` containing exactly 18 hardcoded problems:
     - `odd-or-even-sum`
     - `reverse-a-string`
     - `sum-of-array`
     - `palindrome-check`
     - `prime-numbers-count`
     - `prime-number-check`
     - `check-divisibility-by-7`
     - `next-greater-power-of-2`
     - `vowel-check-in-string`
     - `number-range-check`
     - `round-to-nearest-greater-integer`
     - `string-middle-element-modification`
     - `check-if-number-is-composite`
     - `print-factors-of-a-number`
     - `check-divisibility-by-13`
     - `perfect-square-product`
     - `odd-digits-in-a-number`
     - `ninja-clan-difference`
   - Lines 378–501 define 9 static templates:
     - `TEMPLATE_ARRAY_MIN_MAX`
     - `TEMPLATE_ARRAY_SORT`
     - `TEMPLATE_ARRAY_DEDUPLICATE`
     - `TEMPLATE_MATH_GCD_LCM`
     - `TEMPLATE_MATH_FACTORIAL`
     - `TEMPLATE_MATH_FIBONACCI`
     - `TEMPLATE_STRING_COUNT_VOWELS`
     - `TEMPLATE_KADANE_MAX_SUBARRAY`
     - `TEMPLATE_FALLBACK_ECHO`

3. **Fallback & Keyword Matching Behavior**:
   - Lines 606–643:
     ```python
     full_text = f"{spec.title} {spec.description} {spec.input_spec} {spec.output_spec}".lower()

     if "prime" in full_text and ("count" in full_text or "between" in full_text or "range" in full_text):
         return GeneratedSolution(CANONICAL_SOLVERS["prime-numbers-count"]["code"], "Mathematics", 0.90, "Prime range counter")
     elif "prime" in full_text:
         return GeneratedSolution(CANONICAL_SOLVERS["prime-numbers-count"]["code"], "Mathematics", 0.85, "Prime tester")
     ...
     # 3. Fallback standard solver
     return GeneratedSolution(
         code=TEMPLATE_FALLBACK_ECHO,
         category="General I/O",
         confidence=0.50,
         explanation="Standard I/O fallback solution."
     )
     ```
   - Lines 492–500:
     ```python
     TEMPLATE_FALLBACK_ECHO = (
         "import sys\n\n"
         "def solve():\n"
         "    data = sys.stdin.read().strip()\n"
         "    if data:\n"
         "        print(data)\n\n"
         "if __name__ == '__main__':\n"
         "    solve()\n"
     )
     ```

### 1.2 Model / API Integration & Prompt Construction Status
- **Zero LLM or Generative API Integration**: Inspection of the workspace and virtual environment (`python3 -m pip list`, `grep_search`) confirmed that:
  - No generative AI libraries (`google-genai`, `google.generativeai`, `openai`, `anthropic`, `langchain`) are imported in `zenclass_guvi`.
  - There are no prompt templates, system instructions, or dynamic LLM calls in `solver/code_generator.py`.
  - All existing code generation is 100% deterministic rule-based keyword matching and static string template interpolation.
  - No `GEMINI_API_KEY` or LLM credentials are set in the runtime environment.

### 1.3 Caller & Test Harness Interface Contracts
- **`sub_orch_m2/SCOPE.md` Interface Contract**:
  - `generate_solution(spec: ProblemSpecification, previous_error: Optional[str] = None, attempt: int = 1) -> GeneratedSolution`
  - Returns `GeneratedSolution(code: str, confidence: float, strategy: str, language: str = "PYTHON 3")`.
- **`drivers/guvi_driver.py` (lines 643–651)**:
  ```python
  # 4. Synthesize Python 3 Candidate Solution
  sol: GeneratedSolution = generate_solution(spec)
  logger.info(f"Synthesized Python 3 solution: Category='{sol.category}', Confidence={sol.confidence:.2f}")

  # 5. Local Subprocess Sandbox Validation
  val_result: ValidationResult = test_solution(
      sol.code,
      spec.sample_cases,
      timeout=config.LOCAL_TEST_TIMEOUT_SECONDS,
  )
  ```
- **Existing Unit Tests (`zenclass_guvi/tests/test_m2_solver.py:226–295`)**:
  - Tests verify `generate_solution` and `synthesize_solution` accepting `str`, `dict`, `ProblemSpecification`.
  - Tests assert `isinstance(sol, GeneratedSolution)`, `sol.category`, `sol.confidence`, `sol.explanation`.
  - Tests construct mocks with `GeneratedSolution(code=..., category=..., confidence=..., explanation=...)`.

### 1.4 Test Suite Baseline
- Command: `python3 -m pytest zenclass_guvi/tests/`
- Result: **268 passed in 69.01s** (100% pass rate across Tier 1, Tier 2, Tier 3, Tier 4, and Milestone 1–5 tests).
- All 35 tests in `test_m2_solver.py` passed without error.

---

## 2. Logic Chain

### 2.1 Limitation Analysis: Why Current `solver/code_generator.py` Fails Medium and Hard Problems

1. **The "Echo Trap" on Uncataloged Problems**:
   - *Observation 1.1*: `CANONICAL_SOLVERS` only covers 18 School/Easy problems. The regex keyword matcher only covers 14 simple keywords (`prime`, `palindrome`, `reverse`, `vowel`, `gcd`, `factorial`, `fibonacci`, `kadane`, `sort`, `duplicate`, `min/max`, `sum`, `even/odd`).
   - *Logic*: Medium and Hard problems on Guvi CodeKata (e.g. Graph Traversals, Shortest Paths, Topological Sort, 0/1 Knapsack, Coin Change, Longest Common Subsequence, Binary Search on Answer, Monotonic Stack, Interval Merging, Matrix Spiral, Sieve of Eratosthenes) match none of these 14 simple conditions.
   - *Deduction*: Any Medium or Hard problem automatically falls through to `TEMPLATE_FALLBACK_ECHO`, which simply echoes `sys.stdin.read().strip()`. This produces an immediate `Output mismatch` in the local sandbox test runner (`solver/test_runner.py`), preventing submission or failing platform test cases 100% of the time.

2. **Input Parsing Fragility & Malformed Input Handling**:
   - *Observation 1.1*: All existing templates assume either `tokens = sys.stdin.read().split()` with single-line integers or `raw = sys.stdin.read().strip()`.
   - *Logic*: Medium and Hard problems frequently have complex I/O specifications:
     - First line $N$, second line $N$ space-separated integers, or $N \times M$ matrix rows across $N$ lines.
     - Multiple test cases $T$ on the first line, followed by $T$ blocks of varying lengths.
     - Graph edge lists: $N, M$ followed by $M$ lines of $(u, v)$ or $(u, v, w)$.
     - String lines containing spaces or punctuation.
     - Extractor artifacts: as observed in the live SQLite database (`ValueError: invalid literal for int() with base 10: '{display:inline-flex...'`), unparsed style tags or header tokens can appear in input.
   - *Deduction*: The current single-line token split crashes with `IndexError` or `ValueError` whenever multi-line structures, matrix rows, or non-integer tokens are encountered.

3. **Algorithmic Complexity & Execution Limits**:
   - *Observation 1.1*: None of the templates include recursion limit elevation (`sys.setrecursionlimit`), fast I/O idioms, or $O(N \log N)$ / $O(N)$ data structures (e.g. `heapq`, `collections.deque`, `bisect`).
   - *Logic*: Guvi CodeKata Medium and Hard problems feature input constraints up to $N = 10^5$ or $10^6$ and a strict 1.0–2.0s time limit.
     - Deep recursion without `sys.setrecursionlimit` triggers `RecursionError: maximum recursion depth exceeded`.
     - Trial division for large primes or $O(N^2)$ nested loops triggers `TimeoutExpired` in the sandbox.
   - *Deduction*: Current templates lack the algorithmic scaling and runtime safety flags required for competitive programming constraints.

4. **Signature Disconnect & Missing Error Feedback Refinement**:
   - *Observation 1.1 & 1.3*: `generate_solution` has the signature `def generate_solution(problem: Union[ProblemSpecification, Any]) -> GeneratedSolution:`. It cannot accept `previous_error` or `attempt`.
   - *Observation 1.3*: `drivers/guvi_driver.py` attempts a problem only once; if it fails, it records `FAILED` without retrying. Feature 6 requires `generate_solution(spec, previous_error=..., attempt=...)` across 3 attempts.
   - *Deduction*: Even if `guvi_driver.py` were modified to loop 3 times, passing `previous_error` to the current `generate_solution()` causes a `TypeError: unexpected keyword argument`. Furthermore, `code_generator.py` lacks any error analysis logic to adapt its synthesis based on previous error messages (e.g., switching from quadratic to linear algorithms on `TimeoutExpired`, or adjusting formatting on `Output mismatch`).

5. **Data Contract Discrepancy**:
   - *Observation 1.1 & 1.3*: `GeneratedSolution` currently has `(code, category, confidence, explanation)`.
   - *Observation 1.3*: `SCOPE.md` specifies `GeneratedSolution(code, confidence, strategy, language="PYTHON 3")`.
   - *Observation 1.3*: Existing tests and drivers specifically access `sol.category`, `sol.confidence`, and `sol.explanation`.
   - *Deduction*: To satisfy `SCOPE.md` while maintaining 100% backward compatibility with all 268 tests, `GeneratedSolution` must support `strategy` and `language` with sensible defaults that alias or preserve `category` and `explanation`.

---

## 3. Caveats
1. **Network & External LLM Availability**: External LLM APIs (e.g., Google Gemini API via `google-genai`) are not pre-installed or keyed in the execution environment. Therefore, the core synthesis engine must be **100% autonomous, local, deterministic, and self-contained**. An optional LLM provider can be integrated as an opportunistic plug-in (activated only when `GEMINI_API_KEY` is present), but the system cannot rely on it as a mandatory dependency.
2. **Guvi Hidden Test Cases**: Guvi CodeKata evaluates submissions against hidden test cases. Local sandbox validation against `spec.sample_cases` provides high confidence, but edge cases (e.g. $N=0$, single element, negative numbers, extreme constraints) must be proactively guarded against in the generated code templates.

---

## 4. Conclusion & Recommended Architecture

To satisfy Feature 5 (Medium & Hard Code Generation) and Feature 6 (Solver Retry Feedback Refinement) without causing any regressions in the existing 268 tests, `solver/code_generator.py` must be upgraded to a **6-Layer Adaptive Algorithmic Synthesis Architecture**:

```
+-----------------------------------------------------------------------------------+
|                        6-Layer Adaptive Code Generator                            |
+-----------------------------------------------------------------------------------+
| Layer 1: Canonical Catalog (18 Existing + Medium/Hard Benchmark Solvers)           |
+-----------------------------------------------------------------------------------+
| Layer 2: Algorithmic Taxonomy & Domain Classifier (DP, Graphs, Trees, BS, etc.)    |
+-----------------------------------------------------------------------------------+
| Layer 3: Adaptive Input/Output Parser Generator (Multi-line, Matrix, Token Stream)|
+-----------------------------------------------------------------------------------+
| Layer 4: Error Adaptation Engine (Refines code on Timeout, IndexError, Mismatch)  |
+-----------------------------------------------------------------------------------+
| Layer 5: Local Sandbox Pre-Verification (Runs test_solution on sample_cases)     |
+-----------------------------------------------------------------------------------+
| Layer 6: Optional Plug-and-Play LLM Fallback (Only if GEMINI_API_KEY configured)  |
+-----------------------------------------------------------------------------------+
```

### 4.1 Enhanced Data Models and Signatures

```python
@dataclass
class GeneratedSolution:
    """Represents a synthesized algorithmic code solution with metadata."""
    code: str
    category: str
    confidence: float
    explanation: str
    strategy: str = ""
    language: str = "PYTHON 3"

    def __post_init__(self):
        if not self.strategy:
            self.strategy = self.category
        if not self.category and self.strategy:
            self.category = self.strategy

def generate_solution(
    problem: Union[ProblemSpecification, Any],
    previous_error: Optional[str] = None,
    attempt: int = 1
) -> GeneratedSolution:
    """
    Synthesizes an optimal Python 3 solution for a given problem specification.
    Adapts code synthesis dynamically based on previous_error and attempt number.
    """

def synthesize_solution(
    problem: Union[ProblemSpecification, Any],
    previous_error: Optional[str] = None,
    attempt: int = 1
) -> str:
    """AST-validated contract wrapper returning source code string."""
```

### 4.2 Comprehensive Algorithmic Domain Taxonomy (Layer 2)
The synthesizer must classify problems into comprehensive algorithmic domains with dedicated competitive programming patterns:

| Domain | Key Algorithmic Patterns | Trigger Keywords & Concepts | Target Time Complexity |
|---|---|---|---|
| **Dynamic Programming** | 0/1 Knapsack, Coin Change, LIS ($O(N \log N)$), LCS, Edit Distance, Grid Unique Paths, Min Path Sum | `knapsack`, `coin change`, `subsequence`, `edit distance`, `grid path`, `longest increasing`, `minimum path` | $O(N \cdot W)$, $O(N \log N)$, $O(N \cdot M)$ |
| **Graphs & Trees** | BFS (shortest path in grid/graph), DFS (connected components, islands), Dijkstra (`heapq`), Topological Sort (Kahn's), Cycle Detection, DSU | `graph`, `vertices`, `edges`, `shortest path`, `dijkstra`, `topological`, `islands`, `cycle`, `tree`, `connected components` | $O(V + E \log V)$, $O(V + E)$ |
| **Searching & Two Pointers** | Binary Search on Answer (allocation, min-max capacity), Sliding Window (distinct characters, max sum $K$), Two/Three Sum | `binary search`, `sliding window`, `two pointer`, `subarray sum`, `capacity`, `allocate`, `triplet sum` | $O(N)$, $O(N \log N)$ |
| **Intervals & Monotonic Stacks** | Interval Merging, Meeting Rooms, Next Greater Element, Stock Span, Largest Rectangle in Histogram | `interval`, `overlap`, `meeting`, `next greater`, `histogram`, `stock span`, `monotonic` | $O(N \log N)$, $O(N)$ |
| **Matrix Operations** | Spiral Matrix Traversal, Matrix 90° Rotation, Matrix Search, Boolean Matrix | `matrix`, `2d array`, `spiral`, `rotate 90`, `grid`, `row column` | $O(R \cdot C)$ |
| **Advanced Number Theory** | Sieve of Eratosthenes ($N \le 10^6$), Fast Modular Exponentiation, Prime Factorization, Extended GCD | `prime`, `sieve`, `modulo`, `factorization`, `gcd`, `lcm`, `coprime`, `divisors` | $O(N \log \log N)$, $O(\log N)$ |
| **Strings & Parsing** | Longest Palindromic Substring, Group Anagrams, Valid/Longest Parentheses, String Compression | `palindrome substring`, `anagram`, `parentheses`, `balanced brackets`, `longest valid` | $O(N)$, $O(N \log N)$ |

### 4.3 Adaptive Input/Output Parser Generator (Layer 3)
Instead of hardcoding a single `read().split()`, analyze `spec.sample_cases` and input description to synthesize standard competitive programming I/O:
1. **Safety Boilerplate**: Always include:
   ```python
   import sys
   # Increase recursion depth for deep DFS/DP
   sys.setrecursionlimit(200000)
   ```
2. **Input Structure Detection**:
   - Single line numbers / words $\rightarrow$ `sys.stdin.read().split()`
   - Multi-line / Matrix $\rightarrow$ `lines = [line.strip() for line in sys.stdin.read().strip().splitlines() if line.strip()]`
   - Test cases $T$ on line 1 $\rightarrow$ Iterate test cases cleanly with token pointers.
3. **Output Format Normalization**:
   - Array outputs formatted with `' '.join(map(str, res))` (space-separated) or `'\n'.join(...)`.
   - Boolean queries formatted to match problem expectation: `'yes'/'no'`, `'YES'/'NO'`, or `'true'/'false'`.
   - Floating point outputs formatted to specified decimal places (e.g. `"{:.2f}".format(val)`).

### 4.4 Error Adaptation & Strategy Progression (Layer 4)
When `previous_error` is supplied across retries:
- **Attempt 1 (Direct Domain Synthesis)**:
  - Classify problem based on title, description, constraints, and sample cases.
  - Apply standard optimal template/algorithm with local sandbox validation.
- **Attempt 2 (Targeted Error Adaptation)**:
  - If `previous_error` contains `"TimeoutExpired"` or `"timed out"`:
    - Upgrade algorithm complexity: e.g. switch from trial division to Sieve of Eratosthenes, switch from $O(N^2)$ DP to $O(N \log N)$ binary search, switch from slow recursion to iterative tabulation, replace `input()` with `sys.stdin.read().split()`.
  - If `previous_error` contains `"ValueError"` or `"IndexError"`:
    - Switch to defensive token stream reader that strips non-numeric characters, tolerates empty lines, and guards array index boundaries.
  - If `previous_error` contains `"Output mismatch"`:
    - Re-examine sample case expected output: flip case sensitivity (`'yes'` $\leftrightarrow$ `'YES'`), adjust separator (space vs newline vs comma), or check rounding precision.
  - If `previous_error` contains `"RecursionError"`:
    - Inject `sys.setrecursionlimit(300000)` and convert recursive calls to iterative stack/queue.
- **Attempt 3 (Defensive Heuristic Fallback)**:
  - If specialized algorithm failed both attempts, deploy a robust, highly-defensive fallback tailored to the category that gracefully handles edge cases (empty input, single element, boundary constraints) and passes known sample test cases.

### 4.5 Local Sandbox Pre-Verification (Layer 5)
Before returning `GeneratedSolution`:
- If `spec.sample_cases` contains valid input/expected cases, run `test_solution(candidate_code, spec.sample_cases, timeout=1.5)` using the existing sandboxed runner in `solver/test_runner.py`.
- If the candidate passes all sample cases, confidence is boosted to $\ge 0.95$.
- If it fails, the synthesizer internally tries its secondary template or alternative parsing strategy before returning to the caller.

---

## 5. Verification Method

### 5.1 Independent Reproduction Commands
Run the following commands in the workspace root (`/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi`):

1. **Verify Baseline Test Suite (No Regressions)**:
   ```bash
   python3 -m pytest tests/
   ```
   *Expected Result*: All 268 existing tests pass.

2. **Verify Solver Unit Tests**:
   ```bash
   python3 -m pytest tests/test_m2_solver.py -v
   ```
   *Expected Result*: All 35 tests pass cleanly in under 1.0 second.

3. **Verify AST Validity of All Synthesized Solutions**:
   ```python
   python3 -c "
   import ast
   from solver.code_generator import CANONICAL_SOLVERS, synthesize_solution
   for slug in CANONICAL_SOLVERS:
       code = synthesize_solution(slug)
       ast.parse(code)
   print('All canonical solutions valid AST.')
   "
   ```

### 5.2 Invalidation Conditions
This analysis and recommendation would be invalidated if:
1. Modifying `GeneratedSolution` breaks backward compatibility with existing tests expecting `category` and `explanation`. (Mitigated: default arguments and post-init aliasing preserve all 4 original attributes).
2. Guvi CodeKata requires languages other than Python 3. (Invalidated by ORIGINAL_REQUEST R2: "Python 3 solutions").
3. External LLM network calls are made a mandatory hard dependency without offline fallback. (Mitigated: 100% autonomous local rule-based and template-based engine).
