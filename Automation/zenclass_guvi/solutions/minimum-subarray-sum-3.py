import sys

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        print(0)
        return
    arr = list(map(int, data[1:n+1]))
    min_sum = arr[0]
    current = arr[0]
    for i in range(1, n):
        current = min(arr[i], current + arr[i])
        min_sum = min(min_sum, current)
    print(min_sum)

solve()
