import sys
from collections import deque

def main() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    it = iter(data)
    n = int(next(it))
    m = int(next(it))
    if n == 0:
        print("no")
        return
    if m != n - 1:
        print("no")
        return
    adj = [[] for _ in range(n + 1)]
    for _ in range(m):
        u = int(next(it))
        v = int(next(it))
        adj[u].append(v)
        adj[v].append(u)
    visited = [False] * (n + 1)
    q = deque([1])
    visited[1] = True
    cnt = 1
    while q:
        cur = q.popleft()
        for nb in adj[cur]:
            if not visited[nb]:
                visited[nb] = True
                cnt += 1
                q.append(nb)
    print("yes" if cnt == n else "no")

if __name__ == "__main__":
    main()
