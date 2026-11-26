import sys

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    try:
        R = int(data[0])
    except:
        return
    if R <= 0:
        return
    out_lines = []
    for i in range(1, R + 1):
        line = ' '.join(str(i * j) for j in range(1, i + 1))
        out_lines.append(line)
    sys.stdout.write('\n'.join(out_lines))

if __name__ == "__main__":
    solve()
