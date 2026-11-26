import sys

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    try:
        R = int(data[0])
    except:
        return
    if R <= 0:
        return
    cur = 1
    out_lines = []
    for row in range(1, R + 1):
        nums = list(range(cur, cur + row))
        cur += row
        out_lines.append(' '.join(map(str, nums)))
    sys.stdout.write('\n'.join(out_lines))

if __name__ == "__main__":
    solve()
