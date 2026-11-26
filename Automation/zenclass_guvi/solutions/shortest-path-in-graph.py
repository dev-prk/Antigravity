import sys
from collections import deque

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    it = iter(data)
    n = int(next(it))
    e = int(next(it))
    a = int(next(it))
    
    adj = [[] for _ in range(n + 1)]
    
    for _ in range(e):
        u = int(next(it))
        v = int(next(it))
        adj[u].append(v)
        adj[v].append(u)
    
    if a < 1 or a > n:
        print(-1)
        return
    
    if a == 1:
        print(0)
        return
    
    dist = [-1] * (n + 1)
    q = deque()
    dist[1] = 0
    q.append(1)
    
    while q:
        u = q.popleft()
        if u == a:
            break
        for v in adj[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                q.append(v)
    
    print(dist[a])

if __name__ == "__main__":
    main()
