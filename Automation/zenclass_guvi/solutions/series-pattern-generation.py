import sys

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    try:
        n = int(data[0])
    except:
        return
    if n <= 0:
        # No output for non‑positive n
        return
    res = []
    for k in range(1, n + 1):
        t = k * (k + 1) // 2
        res.append(str(t * t))
    sys.stdout.write(' '.join(res))

if __name__ == "__main__":
    solve()
