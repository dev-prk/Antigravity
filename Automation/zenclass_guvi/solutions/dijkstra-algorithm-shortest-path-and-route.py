import sys, heapq

def solve() -> None:
    data = list(map(int, sys.stdin.read().strip().split()))
    if not data:
        return
    idx = 0
    n = data[idx]; idx += 1
    total = n * n
    matrix = data[idx:idx + total]
    idx += total
    if idx + 1 >= len(data):
        return
    s = data[idx]; d = data[idx + 1]

    adj = [[] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            w = matrix[i * n + j]
            if w != 0:
                adj[i].append((j, w))

    INF = 10**18
    dist = [INF] * n
    prev = [-1] * n
    dist[s] = 0
    heap = [(0, s)]
    while heap:
        cur_dist, u = heapq.heappop(heap)
        if cur_dist != dist[u]:
            continue
        if u == d:
            break
        for v, w in adj[u]:
            nd = cur_dist + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))

    if dist[d] == INF:
        sys.stdout.write("No path")
        return

    path = []
    v = d
    while v != -1:
        path.append(v)
        if v == s:
            break
        v = prev[v]
    path.reverse()
    sys.stdout.write(' '.join(map(str, path)) + '\n')
    sys.stdout.write(str(dist[d]))

if __name__ == "__main__":
    solve()
