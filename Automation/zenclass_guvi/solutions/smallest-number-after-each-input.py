import sys
import heapq

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    numbers = list(map(int, data[1:1+n]))
    
    heap = []
    result = []
    
    for num in numbers:
        heapq.heappush(heap, num)
        result.append(str(heap[0]))
    
    print(' '.join(result))

if __name__ == "__main__":
    main()
