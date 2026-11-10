#!/usr/bin/env python3
"""
harness_2_ast_extreme.py - Empirical Stress Harness for AST Validity Under Extreme and Adversarial Inputs.

Adversarially tests synthesize_solution and generate_solution with:
1. Empty inputs (empty string, whitespace string, empty ProblemSpecification)
2. Huge inputs (10,000 chars, 50,000 chars of garbage, repeating characters)
3. Binary and non-ASCII payloads (null bytes, control chars, emojis, unicode surrogate pairs)
4. Code injection attacks (raw Python syntax errors, triple quotes, exec/eval payloads)
5. SQL / Shell injection strings
6. Malformed and unexpected data types (None, ints, dicts with invalid structures, floats, bytes)
7. Compilation check: compile(code, '<test>', 'exec') must always succeed.
"""

import ast
import random
import string
import sys

BASE_DIR = "/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from solver.extractor import ProblemSpecification, ProblemSpec, SampleCase
from solver.code_generator import synthesize_solution, generate_solution


def test_ast_validity():
    print("=" * 70)
    print("STARTING HARNESS 2: AST Validity Under Extreme & Adversarial Inputs")
    print("=" * 70)

    adversarial_inputs = [
        ("Empty string", ""),
        ("Whitespace only", "    \n\t  \r\n  "),
        ("Single char 'a'", "a"),
        ("Single char 'z'", "z"),
        ("Empty ProblemSpecification", ProblemSpecification(title="", description="", input_spec="", output_spec="")),
        ("None input", None),
        ("Integer input", 999999),
        ("Float input", 3.1415926535),
        ("Bytes input", b"\x00\x01\x02\xff\xfe\xab"),
        ("Dict empty", {}),
        ("Dict with corrupted keys", {"corrupt": None, 123: 456, "sample_cases": [None, 42, {}]}),
        ("10,000 char random ASCII", "".join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=10000))),
        ("50,000 char repeating 'A'", "A" * 50000),
        ("10,000 char newlines", "\n" * 10000),
        ("Python code injection in title", "__import__('os').system('echo hacked')\nimport sys\nsys.exit(1)"),
        ("Syntax error in title", "def broken_code(::):\n return }}}"),
        ("Triple quotes inside description", "''' \"\"\" ''' \"\"\" \'\'\' \"\"\""),
        ("SQL injection string", "'; DROP TABLE tasks; DROP TABLE users; --"),
        ("Shell injection string", "$(rm -rf /) `cat /etc/passwd` & touch /tmp/pwned"),
        ("XSS payload in HTML", "<script>alert('xss');</script><img src=x onerror=alert(1)>"),
        ("Null bytes and control chars", "problem\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0e\x0f\x7f"),
        ("Complex unicode and emojis", "🚀🔥🤖 CodeKata Задача 123! 日本語 tested \U0001F600 \u200b\u200c\u200d\ufeff"),
        ("Nested brackets and special syntax", "{{{{[[[((((:::;;;<<<>>>???))))]]]}}}}"),
        ("Adversarial problem spec with all fields corrupted", ProblemSpecification(
            title="""'; SELECT * FROM "WHERE '1'='1' \x00 """,
            description="""Triple quotes ''' and \"\"\" and code: def f(): return 1+""",
            input_spec="\\x00\\xff\\xfe\n\t\r",
            output_spec="None\n\n\n" * 100,
            sample_cases=[SampleCase(input_text="bad\x00data", expected_output="corrupt\x00out")],
            constraints="O(1) " * 500,
            category="Hacking/Exploit",
            raw_text="<!-- broken comment",
            _slug="adversarial-slug-with-symbols-!@#$%^&*()"
        ))
    ]

    all_passed = True
    results = []

    for idx, (label, inp) in enumerate(adversarial_inputs, 1):
        print(f"[{idx:02d}/{len(adversarial_inputs):02d}] Testing: {label[:45]:<45}", end=" ")
        try:
            # 1. Test generate_solution
            gen_res = generate_solution(inp)
            if not gen_res or not gen_res.code:
                print("-> [FAIL: Empty generated solution]")
                all_passed = False
                results.append((label, False, "Empty code"))
                continue

            # 2. Test synthesize_solution contract
            code_str = synthesize_solution(inp)
            if not isinstance(code_str, str) or not code_str.strip():
                print("-> [FAIL: synthesize_solution did not return non-empty str]")
                all_passed = False
                results.append((label, False, "Empty synthesize_solution str"))
                continue

            # 3. Test ast.parse
            tree = ast.parse(code_str)

            # 4. Test code compilation
            compiled = compile(code_str, f"<adversarial_{idx}>", "exec")

            print("-> [PASS: Valid AST & Compiles]")
            results.append((label, True, "OK"))

        except SyntaxError as se:
            print(f"-> [FAIL: SyntaxError: {se}]")
            all_passed = False
            results.append((label, False, f"SyntaxError: {se}"))
        except Exception as ex:
            print(f"-> [FAIL: Exception: {type(ex).__name__}: {ex}]")
            all_passed = False
            results.append((label, False, f"Exception: {type(ex).__name__}"))

    print("\n" + "=" * 70)
    print("HARNESS 2 SUMMARY:")
    passed_count = sum(1 for _, ok, _ in results if ok)
    print(f"Total Tests: {len(results)}, Passed: {passed_count}, Failed: {len(results) - passed_count}")
    print(f"OVERALL HARNESS 2: {'PASSED' if all_passed else 'FAILED'}")
    print("=" * 70)
    return all_passed


if __name__ == "__main__":
    success = test_ast_validity()
    sys.exit(0 if success else 1)
