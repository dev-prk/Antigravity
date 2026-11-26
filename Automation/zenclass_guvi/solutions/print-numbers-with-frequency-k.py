import sys
from collections import Counter

def solve() -> None:
    data = sys.stdin.read().split()
    if not data:
        return
    N = int(data[0])
    K = int(data[1])
    if N == 0:
        return
    arr = list(map(int, data[2:2+N]))
    freq = Counter(arr)
    result = [num for num in freq if freq[num] < K]
    result.sort()
    print(' '.join(map(str, result)))

if __name__ == "__main__":
    solve()
