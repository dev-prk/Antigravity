import sys

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    arr = list(map(int, data[1:1 + n]))
    arr.sort()
    # Sum of the two smallest elements
    print(arr[0] + arr[1])

if __name__ == "__main__":
    solve()
