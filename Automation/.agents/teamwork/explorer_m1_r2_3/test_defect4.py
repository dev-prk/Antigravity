import re

raw_html = """
<style>
.editor { font-family: monospace; }
<section>Problem Statement: Calculate factorial of n.</section>
<p>Sample Input: 5</p>
<p>Sample Output: 120</p>
"""

TAG_LIST_OLD = r"(?:p|div|h[1-6]|span|body|html|br|pre|table|ul|li)"
TAG_LIST_NEW = r"(?:p|div|h[1-6]|span|body|html|br|pre|table|ul|li|section|article|main|aside|header|footer|nav)"

text_old = re.sub(
    rf"(?is)<(script|style|noscript|svg|template)\b[^>]*>.*?(?:</\s*\1\s*>|(?=<{TAG_LIST_OLD}\b)|$)",
    " ",
    raw_html,
)
text_new = re.sub(
    rf"(?is)<(script|style|noscript|svg|template)\b[^>]*>.*?(?:</\s*\1\s*>|(?=<{TAG_LIST_NEW}\b)|$)",
    " ",
    raw_html,
)

print("Old stripped output:")
print(repr(text_old.strip()))
print("New stripped output:")
print(repr(text_new.strip()))
assert "Calculate factorial of n." not in text_old
assert "Calculate factorial of n." in text_new
print("Defect 4 verification successful!")
