import sys
import heapq

def main():
    data = sys.stdin.read().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    q = int(data[1])
    ropes = list(map(int, data[2:2+n]))
    
    if q == 0:
        print(sum(ropes))
        return
    
    total = sum(ropes)
    
    # Min heap: (amount that would be cut, current length of rope)
    heap = []
    for l in ropes:
        if l > 0:
            # Amount that would be cut if we cut this rope
            cut_amount = (l + 1) // 2
            heapq.heappush(heap, (cut_amount, l))
    
    cuts = 0
    while cuts < q and heap:
        cut_amount, length = heapq.heappop(heap)
        
        total -= cut_amount
        cuts += 1
        
        new_length = length - cut_amount
        
        if new_length > 0:
            new_cut_amount = (new_length + 1) // 2
            heapq.heappush(heap, (new_cut_amount, new_length))
    
    print(total)

if __name__ == "__main__":
    main()
