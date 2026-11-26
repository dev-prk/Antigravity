import sys

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    days = int(data[0])
    items = list(map(int, data[1:1 + days]))
    total = sum(items)
    avg = total // days
    print(total)
    print(avg)

if __name__ == "__main__":
    solve()
