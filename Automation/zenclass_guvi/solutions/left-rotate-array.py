import sys

def solve():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    k = int(data[1])
    if n == 0:
        return
    arr = list(map(int, data[2:2+n]))
    k = k % n
    if k == 0:
        result = arr
    else:
        result = arr[k:] + arr[:k]
    print(' '.join(map(str, result)))

t = None
solve()
