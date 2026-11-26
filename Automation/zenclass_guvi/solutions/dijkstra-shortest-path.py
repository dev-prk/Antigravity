import sys
import heapq

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    m = int(data[1])
    
    graph = [[] for _ in range(n)]
    index = 2
    
    for _ in range(m):
        u = int(data[index])
        v = int(data[index + 1])
        w = int(data[index + 2])
        graph[u].append((v, w))
        index += 3
    
    source = int(data[index])
    
    INF = float('inf')
    dist = [INF] * n
    dist[source] = 0
    
    pq = [(0, source)]
    
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in graph[u]:
            if dist[v] > dist[u] + w:
                dist[v] = dist[u] + w
                heapq.heappush(pq, (dist[v], v))
    
    result = []
    for d in dist:
        if d == INF:
            result.append(str(-1))
        else:
            result.append(str(d))
    
    print(' '.join(result))

if __name__ == "__main__":
    main()
