import sys

def is_adam(n):
    n = abs(n)
    rev = lambda x: int(str(x)[::-1])
    rev_n = rev(n)
    rev_sq = rev(n * n)
    return rev_sq == rev_n * rev_n

data = sys.stdin.read().strip().split()
if data:
    n = int(data[0])
    print("Yes" if is_adam(n) else "No")
