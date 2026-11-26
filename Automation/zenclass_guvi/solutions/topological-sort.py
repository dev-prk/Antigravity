import sys
from collections import deque

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    m = int(data[1])
    
    adj = [[] for _ in range(n)]
    in_degree = [0] * n
    
    idx = 2
    for _ in range(m):
        u = int(data[idx])
        v = int(data[idx + 1])
        adj[u].append(v)
        in_degree[v] += 1
        idx += 2
    
    q = deque()
    for i in range(n):
        if in_degree[i] == 0:
            q.append(i)
    
    result = []
    while q:
        u = q.popleft()
        result.append(u)
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                q.append(v)
    
    print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
