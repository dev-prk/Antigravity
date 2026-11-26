s = input().strip()
valid_chars = set("0123456789ABCDEFabcdef")
print("yes" if s and all(c in valid_chars for c in s) else "no")
