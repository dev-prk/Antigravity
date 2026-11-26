import sys
import heapq

def prim_mst_cost():
    data = sys.stdin.read().split()
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
        index += 3
        graph[u].append((v, w))
        graph[v].append((u, w))
    
    visited = [False] * n
    min_heap = []
    heapq.heappush(min_heap, (0, 0))
    
    total_cost = 0
    edges_used = 0
    
    while min_heap and edges_used < n:
        weight, u = heapq.heappop(min_heap)
        
        if visited[u]:
            continue
        
        visited[u] = True
        total_cost += weight
        edges_used += 1
        
        for v, w in graph[u]:
            if not visited[v]:
                heapq.heappush(min_heap, (w, v))
    
    print(total_cost)

if __name__ == "__main__":
    prim_mst_cost()
