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

    even_line = ("BA" * ((n + 1) // 2))[:n]
    odd_line = ("AB" * ((n + 1) // 2))[:n]

    out_lines = []
    for i in range(n):
        out_lines.append(even_line if i % 2 == 0 else odd_line)
    sys.stdout.write("\n".join(out_lines))

if __name__ == "__main__":
    solve()
