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
        return

    lines = []
    last = n - 1
    for i in range(n):
        row_vals = []
        for j in range(n):
            val = max(i, last - i, j, last - j) + 1
            row_vals.append(str(val))
        lines.append(' '.join(row_vals))
    sys.stdout.write('\n'.join(lines))

if __name__ == "__main__":
    solve()
