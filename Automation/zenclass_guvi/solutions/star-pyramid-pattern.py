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
    out_lines = []
    for i in range(1, n + 1):
        out_lines.append(' '.join(['*'] * i))
    sys.stdout.write('\n'.join(out_lines))

if __name__ == "__main__":
    solve()
