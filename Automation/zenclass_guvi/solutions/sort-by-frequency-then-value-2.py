import sys
from collections import Counter

def solve():
    n = int(sys.stdin.readline().strip())
    arr = list(map(int, sys.stdin.readline().strip().split()))
    
    if n == 0 or len(arr) == 0:
        print(-1)
        return
    
    freq = Counter(arr)
    
    sorted_items = sorted(freq.items(), key=lambda x: (x[1], x[0]))
    
    result = []
    for num, count in sorted_items:
        result.extend([str(num)] * count)
    
    print(' '.join(result))

if __name__ == "__main__":
    solve()
