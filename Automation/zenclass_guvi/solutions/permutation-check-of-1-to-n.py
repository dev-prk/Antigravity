import sys

def solve() -> None:
    data = list(map(int, sys.stdin.read().strip().split()))
    if not data:
        return
    n = data[0]
    arr = data[1:1 + n] if n >= 0 else []
    if len(arr) != n:
        print("no")
        return
    if n == 0:
        print("yes")
        return
    if set(arr) == set(range(1, n + 1)):
        print("yes")
    else:
        print("no")

if __name__ == "__main__":
    solve()
