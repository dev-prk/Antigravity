import sys
import math

def solve() -> None:
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    if n <= 1:
        print("no")
        return
    limit = int(math.isqrt(n))
    for i in range(2, limit + 1):
        if n % i == 0:
            print("yes")
            return
    print("no")

if __name__ == "__main__":
    solve()
