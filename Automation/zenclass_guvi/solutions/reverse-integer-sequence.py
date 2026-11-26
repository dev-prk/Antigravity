import sys

def solve() -> None:
    data = sys.stdin.read().strip()
    if not data:
        return
    try:
        n = int(data.split()[0])
    except:
        return
    if n >= 1:
        seq = range(n, 0, -1)
    else:
        seq = range(n, 2)  # up to and including 1
    out = "\n".join(str(i) for i in seq)
    sys.stdout.write(out)

if __name__ == "__main__":
    solve()
