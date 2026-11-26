import sys
from collections import deque

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    w = int(data[1])
    
    if n == 0 or w == 0:
        print(-1)
        return
    
    arr = list(map(int, data[2:2+n]))
    
    result = []
    dq = deque()
    
    for i in range(n):
        if dq and dq[0] < i - w + 1:
            dq.popleft()
        
        if arr[i] == 0:
            dq.append(i)
        
        if i >= w - 1:
            if dq:
                result.append(str(dq[0] + 1))
            else:
                result.append(str(-1))
    
    print(' '.join(result))

if __name__ == "__main__":
    main()
