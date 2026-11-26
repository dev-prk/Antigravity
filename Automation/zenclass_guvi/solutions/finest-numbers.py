import sys
import math

def is_fine(n):
    if n < 2:
        return False
    t = int(round((n / 2) ** (1/3))) - 1
    for i in range(max(1, t - 5), t + 10):
        val = i**3 + (i + 1)**3
        if val == n:
            return True
        if val > n:
            break
    return False

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    z = int(data[0])
    if z <= 0:
        print(-1)
        return
    arr = list(map(int, data[1:1+z]))
    finest = sorted([x for x in arr if is_fine(x)])
    if not finest:
        print(-1)
    else:
        print(' '.join(map(str, finest)))

if __name__ == "__main__":
    main()
