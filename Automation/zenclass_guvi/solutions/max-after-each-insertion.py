import sys
import heapq
from collections import Counter

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    k = int(data[1])
    
    main_arr = list(map(int, data[2:2+n]))
    additional = list(map(int, data[2+n:2+n+k]))
    
    if n == 0 and k == 0:
        print("")
        return
    
    freq = Counter(main_arr)
    max_heap = [-x for x in main_arr]
    heapq.heapify(max_heap)
    
    result = []
    
    for val in additional:
        freq[val] += 1
        heapq.heappush(max_heap, -val)
        
        while max_heap and freq[-max_heap[0]] == 0:
            heapq.heappop(max_heap)
        
        if max_heap:
            result.append(str(-max_heap[0]))
        else:
            result.append("0")
    
    print(" ".join(result))

solve()
