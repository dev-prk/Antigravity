import sys

s = sys.stdin.readline().strip()
engine_number = sum(int(c) for c in s if c.isdigit())
print(engine_number)
