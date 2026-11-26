import sys
from collections import Counter

def solve():
    s = sys.stdin.readline().strip()
    if not s:
        print(0)
        return
    cnt = Counter(s)
    max_freq = max(cnt.values())
    if max_freq > 1:
        print(max_freq)
    else:
        print(0)

if __name__ == "__main__":
    solve()
