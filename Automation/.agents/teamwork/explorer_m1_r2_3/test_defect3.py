import re

CSS_PROP_PATTERN = (
    r"(?:display|position|flex|margin|padding|color|background|font|font-size|"
    r"font-family|line-height|border|width|height|z-index|overflow|opacity|"
    r"visibility|align-items|justify-content|box-sizing|cursor|outline|"
    r"pointer-events|transition|transform|animation|white-space|text-align|"
    r"vertical-align|user-select)"
)

CSS_RULE_RE = re.compile(
    rf"(?:^|\n)\s*(?![^\{{\n]*(?:Sample|Case|Input\s*[:\-](?!\:)|Output\s*[:\-](?!\:)|Description|Problem))"
    rf"(?:[.#a-zA-Z0-9_\-,>+~\[\]\=\"\'\s]+?(?:::[a-z\-]+|:[a-z\-]+(?:\([^\)]*\))?)*)\s*"
    rf"\{{[^{{}}]*?(?:(?<![\"\'\w-]){CSS_PROP_PATTERN}\s*:\s*[^;{{}}]+(?:;|\b|\}}))[^{{}}]*?\}}",
    re.IGNORECASE | re.DOTALL,
)

test_strings = [
    ("output::after { content: ' '; position: absolute; }", True),
    ("div.card { border: 1px solid black; }", True),
    ("span.badge { display: inline-block; }", True),
    ("div#container { width: 100%; }", True),
    ("input { display: inline-flex; }", True),
    ("output { display: block; margin: 10px; }", True),
    ("Sample Output: 42", False),
    ("Output: 42", False),
    ("Problem Statement: Do something", False),
]

for s, expected in test_strings:
    matched = bool(CSS_RULE_RE.search(s))
    print(f"{s[:40]:40} -> matched={matched} (expected {expected})")
    assert matched == expected, f"Failed on {s}"
print("All CSS_RULE_RE tests passed!")
