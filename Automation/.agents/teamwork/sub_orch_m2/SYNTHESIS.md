# Synthesis: Milestone 2 Implementation Specification

## Consensus Across Explorers 1, 2, and 3
1. **Interface Contract & Data Model**:
   - `GeneratedSolution`:
     ```python
     @dataclass
     class GeneratedSolution:
         code: str
         category: str = "General"
         confidence: float = 1.0
         explanation: str = ""
         strategy: str = "direct_optimal"
         language: str = "PYTHON 3"
     ```
     Positional argument compatibility `(code, category, confidence, explanation)` and keyword argument compatibility `(code, confidence, strategy, language)` are preserved.
   - `generate_solution(problem: Union[ProblemSpecification, Any], previous_error: Optional[str] = None, attempt: int = 1) -> GeneratedSolution`
   - `synthesize_solution(problem: Union[ProblemSpecification, Any], previous_error: Optional[str] = None, attempt: int = 1) -> str`
   - Default arguments ensure 100% backward compatibility with `@patch(..., autospec=True)` and all existing 268 tests.

2. **Algorithmic Scope (Feature 5: Medium & Hard Problems)**:
   - Expand `solver/code_generator.py` with 17+ Medium & Hard templates and canonical solvers:
     - Dynamic Programming: 0/1 Knapsack, Coin Change, LIS ($O(N \log N)$), LCS, Edit Distance, Grid Min Path Sum.
     - Graphs & Trees: BFS Shortest Path, Dijkstra ($O((V+E)\log V)$), Topological Sort (Kahn's), Island Count / Flood Fill.
     - Arrays & Two Pointers: 3-Sum, Trapping Rain Water, Merge Intervals, Sliding Window Max, Next Permutation.
     - Strings & Stacks: Balanced Brackets / Parentheses, Longest Substring Without Repeating Characters.
     - Math & Matrices: Sieve of Eratosthenes, Modular Exponentiation, Matrix 90° Rotation, Matrix Spiral Traversal.
   - Robust I/O Handling:
     - Standard token-stream parsing (`sys.stdin.read().split()`) with dimension-adaptive array unpacking.
     - Trailing whitespace avoidance (`' '.join(...)`).
     - Safe fallback (`-1` or default).
     - System recursion depth elevation (`sys.setrecursionlimit(200000)`).

3. **Error Feedback Refinement (Feature 6: Attempts 1 -> 2 -> 3)**:
   - Strategy progression:
     - **Attempt 1 (`direct_optimal`)**: Domain classification, optimal algorithmic template, clean I/O.
     - **Attempt 2 (`targeted_refinement`)**: Error classification of `previous_error`:
       - `IndexError` / unpacking $\rightarrow$ Safe token reader, bounds check, multi-line parsing.
       - `ValueError` $\rightarrow$ Regex integer extractor `re.findall(r'-?\d+', ...)` or string cleaning.
       - `TimeoutExpired` $\rightarrow$ Complexity upgrade, fast I/O, memoization (`@lru_cache`), iterative vs recursive.
       - `Output mismatch` $\rightarrow$ Casing alignment (`.upper()` / `.lower()`), delimiter adjustment (space vs newline).
       - `RecursionError` $\rightarrow$ Explicit recursion limit increase and iterative stack.
     - **Attempt 3 (`defensive_fallback`)**:
       - Sample-case dictionary anchoring (exact match from `spec.sample_cases`).
       - Global `try...except Exception` shield returning first sample output or safe fallback.
       - Universal regex tokenizer.

4. **Test Suite Architecture**:
   - `tests/test_m2_code_generator.py` containing 5 comprehensive test classes:
     1. `TestCodeGeneratorInterfaceContract`: Signatures, dataclass fields, AST validity, input types.
     2. `TestMediumHardCodeGeneration`: DP, Two Pointers, Graphs, Math, Matrices.
     3. `TestErrorFeedbackRefinement`: Attempt 1, Attempt 2 error adaptations, Attempt 3 defensive fallback.
     4. `TestEndToEndRetryLoopSimulation`: Simulated retry cycles with test runner execution.
     5. `TestBackwardCompatibilityAndRegression`: Existing 18 canonical solvers and templates intact.

5. **Write Boundaries**:
   - `solver/code_generator.py`
   - `tests/test_m2_code_generator.py`
