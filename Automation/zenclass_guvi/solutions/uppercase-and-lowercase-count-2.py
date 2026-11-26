import sys

s = sys.stdin.readline().rstrip('\n')
upper = sum(1 for c in s if c.isupper())
lower = sum(1 for c in s if c.islower())
print(f"{upper} {lower}")
