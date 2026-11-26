import sys

def solve():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    if n <= 0 or 2 * n > len(data) - 1:
        return
    x = map(int, data[1:1+n])
    y = map(int, data[1+n:1+2*n])
    res = [str(a + b) for a, b in zip(x, y)]
    print(' '.join(res))

if __name__ == "__main__":
    solve()
