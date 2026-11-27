import sys
from collections import deque

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    if n == 0:
        print(-1)
        return
    if n == 1:
        print(0)
        return
    
    arr = list(map(int, data[1:n+1]))
    
    jumps = 0
    current_end = 0
    furthest = 0
    
    for i in range(n - 1):
        furthest = max(furthest, i + arr[i])
        
        if i == current_end:
            jumps += 1
            current_end = furthest
            
            if current_end >= n - 1:
                break
    
    print(jumps)

if __name__ == "__main__":
    main()
