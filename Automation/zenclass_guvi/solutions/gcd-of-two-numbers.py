import sys

def gcd(a, b):
    while b:
        a, b = b, a % b
    return abs(a)

data = sys.stdin.read().strip().split()
if len(data) < 2:
    print(-1)
else:
    try:
        n = int(data[0])
        m = int(data[1])
    except ValueError:
        print(-1)
        sys.exit(0)
    if n == 0 or m == 0:
        print(-1)
    else:
        print(gcd(n, m))
