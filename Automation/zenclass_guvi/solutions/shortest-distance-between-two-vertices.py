import sys
import heapq

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    it = iter(data)
    n = int(next(it))
    m = int(next(it))
    
    graph = [[] for _ in range(n)]
    
    for _ in range(m):
        u = int(next(it))
        v = int(next(it))
        cost = int(next(it))
        graph[u].append((v, cost))
    
    source = int(next(it))
    dest = int(next(it))
    
    if source == dest:
        print(0)
        return
    
    INF = float('inf')
    dist = [INF] * n
    dist[source] = 0
    
    heap = [(0, source)]
    
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, cost in graph[u]:
            if dist[v] > dist[u] + cost:
                dist[v] = dist[u] + cost
                heapq.heappush(heap, (dist[v], v))
    
    if dist[dest] == INF:
        print(-1)
    else:
        print(dist[dest])

if __name__ == "__main__":
    main()
