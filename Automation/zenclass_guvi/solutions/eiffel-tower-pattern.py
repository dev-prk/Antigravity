import sys

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    try:
        n = int(data[0])
    except:
        return
    
    out_lines = []
    for i in range(1, n + 1):
        digit = str(i)
        count = 2 * i - 1
        line = digit * count
        # Repeat each digit line (n - i + 1) times
        repeat = n - i + 1
        for _ in range(repeat):
            out_lines.append(line)
    
    print('\n'.join(out_lines))

if __name__ == "__main__":
    solve()
