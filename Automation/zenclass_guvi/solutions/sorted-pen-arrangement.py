import sys

def solve() -> None:
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    new_pens = list(map(int, data[1:1 + n]))
    m = int(data[1 + n])
    present = list(map(int, data[2 + n:2 + n + m]))
    all_pens = new_pens + present
    all_pens.sort()
    print(" ".join(map(str, all_pens)))

if __name__ == "__main__":
    solve()
