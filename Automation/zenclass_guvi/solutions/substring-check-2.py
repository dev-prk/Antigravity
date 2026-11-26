import sys

def solve() -> None:
    data = sys.stdin.read().split()
    if len(data) < 2:
        return
    first = data[0]
    second = data[1]
    if second in first:
        print("yes")
    else:
        print("no")

if __name__ == "__main__":
    solve()
