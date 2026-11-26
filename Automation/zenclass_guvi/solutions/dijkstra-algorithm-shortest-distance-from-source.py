import sys
import heapq

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    matrix = []
    index = 1
    
    for i in range(n):
        row = list(map(int, data[index:index + n]))
        matrix.append(row)
        index += n
    
    s = int(data[index])
    
    adj = [[] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if matrix[i][j] > 0:
                adj[i].append((j, matrix[i][j]))
    
    INF = float('inf')
    dist = [INF] * n
    dist[s] = 0
    
    pq = [(0, s)]
    
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if dist[v] > dist[u] + w:
                dist[v] = dist[u] + w
                heapq.heappush(pq, (dist[v], v))
    
    for i in range(n):
        if dist[i] == INF:
            print(-1)
        else:
            print(dist[i])

if __name__ == "__main__":
    main()
