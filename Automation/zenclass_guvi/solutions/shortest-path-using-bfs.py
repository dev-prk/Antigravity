import sys
from collections import deque

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    it = iter(data)
    try:
        n = int(next(it))
        m = int(next(it))
    except StopIteration:
        return
    
    adj = [[] for _ in range(n)]
    for _ in range(m):
        try:
            u = int(next(it))
            v = int(next(it))
        except StopIteration:
            break
        if 0 <= u < n and 0 <= v < n:
            adj[u].append(v)
            adj[v].append(u)
        # If vertices out of range? Problem likely guarantees valid, but to be safe ignore or handle.
    try:
        source = int(next(it))
    except StopIteration:
        source = 0
    
    dist = [-1] * n
    if 0 <= source < n:
        dist[source] = 0
        q = deque([source])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if dist[v] == -1:
                    dist[v] = dist[u] + 1
                    q.append(v)
    
    sys.stdout.write(" ".join(map(str, dist)))

if __name__ == "__main__":
    main()
