import sys
from collections import deque

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    
    try:
        N = int(data)
    except ValueError:
        N = int(float(data))
    
    if N < 1:
        return
    
    q = deque(['1'])
    result = []
    
    for _ in range(N):
        node = q.popleft()
        result.append(node)
        q.append(node + '0')
        q.append(node + '1')
    
    sys.stdout.write(' '.join(result) + ' ')

if __name__ == "__main__":
    main()
