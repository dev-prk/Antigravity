import sys

s = sys.stdin.readline().strip()
unique_chars = len(set(s))

if unique_chars == 3:
    print("Wonder")
else:
    print(-1)
