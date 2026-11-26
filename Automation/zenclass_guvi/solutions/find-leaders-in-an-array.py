import sys

def solve():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    arr = list(map(int, data[1:1 + n]))
    leaders = []
    max_right = None
    for i in range(len(arr) - 1, -1, -1):
        if max_right is None or arr[i] >= max_right:
            leaders.append(arr[i])
            max_right = arr[i]
    leaders.reverse()
    print(*leaders)

if __name__ == "__main__":
    solve()
