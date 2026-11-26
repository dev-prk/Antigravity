import sys

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    arr = list(map(int, data[1:1 + n]))
    total = sum(arr)
    left = 0
    for x in arr:
        if left == total - left - x:
            print("yes")
            return
        left += x
    print("no")

if __name__ == "__main__":
    solve()
