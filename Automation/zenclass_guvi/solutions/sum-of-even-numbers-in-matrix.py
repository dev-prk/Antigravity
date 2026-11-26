import sys

def solve() -> None:
    data = sys.stdin.read().split()
    if len(data) < 2:
        return
    n = int(data[0])
    m = int(data[1])
    total = 0
    count = n * m
    for i in range(2, 2 + count):
        if i < len(data):
            val = int(data[i])
            if val % 2 == 0:
                total += val
    print(total)

if __name__ == "__main__":
    solve()
