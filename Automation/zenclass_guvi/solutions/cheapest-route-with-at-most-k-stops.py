import sys

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    it = iter(data)
    N = int(next(it))
    M = int(next(it))
    edges = []
    for _ in range(M):
        u = int(next(it))
        v = int(next(it))
        w = int(next(it))
        edges.append((u, v, w))
    src = int(next(it))
    dst = int(next(it))
    K = int(next(it))

    INF = 10**18
    dist = [INF] * N
    dist[src] = 0

    # relax up to K+1 edges (at most K stops)
    for _ in range(K + 1):
        new_dist = dist[:]  # cannot use more than current step edges
        updated = False
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < new_dist[v]:
                new_dist[v] = dist[u] + w
                updated = True
        if not updated:
            break
        dist = new_dist

    ans = dist[dst]
    print(-1 if ans == INF else ans)


if __name__ == "__main__":
    solve()
