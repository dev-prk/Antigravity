import sys
from collections import Counter

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    if n == 0:
        print(-1)
        return
    
    arr = list(map(int, data[1:n+1]))
    
    if n == 1:
        print(-1)
        return
    
    freq = Counter(arr)
    
    max_length = 0
    for num, count in freq.items():
        if count >= 2:
            max_length = max(max_length, count)
    
    if max_length >= 2:
        print(max_length)
    else:
        print(-1)

if __name__ == "__main__":
    solve()
