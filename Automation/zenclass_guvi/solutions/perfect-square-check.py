import sys
from math import isqrt

data = sys.stdin.read().split()
if not data:
    sys.exit(0)

n = int(data[0])

if n < 0:
    print("No")
else:
    r = isqrt(n)
    print("Yes" if r * r == n else "No")
