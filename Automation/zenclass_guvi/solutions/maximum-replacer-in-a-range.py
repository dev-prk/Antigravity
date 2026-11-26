import sys
import math
from functools import reduce

def gcd(a, b):
    return math.gcd(a, b)

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    idx = 0
    n = int(data[idx])
    idx += 1
    
    arr = list(map(int, data[idx:idx+n]))
    idx += n
    
    q = int(data[idx])
    idx += 1
    
    results = []
    
    for _ in range(q):
        l = int(data[idx])
        r = int(data[idx+1])
        idx += 2
        
        segment = arr[l-1:r]
        
        if len(segment) == 0:
            results.append(0)
        elif len(segment) == 1:
            results.append(segment[0])
        else:
            g = reduce(gcd, segment)
            results.append(g)
    
    for res in results:
        print(res)

if __name__ == "__main__":
    solve()
