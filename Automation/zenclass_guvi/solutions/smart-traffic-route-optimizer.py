import sys
import heapq

def solve():
    data = sys.stdin.read().split()
    if not data:
        return
    it = iter(data)
    n = int(next(it))
    m = int(next(it))
    # roads 1-indexed
    roads = [None] * (m + 1)
    # adjacency list: node -> list of (neighbor, cost, road_index) maybe not need road_index
    # For updates, we need to update cost. Since we rebuild adjacency per query or update in place?
    # Simpler: store edges list, and build adjacency fresh for each query? That's O(M) per query plus Dijkstra.
    # Or maintain adjacency and update the specific edge cost. But multiple edges can exist between same u,v with different road ids.
    # Easiest: store all edges with current cost. For each query, build adjacency from edges and run Dijkstra.
    # Building adjacency O(M), Dijkstra O(M log N). Total O(Q*(M + M log N)). Fine for easy.
    
    # travel_time constant per road, congestion mutable
    travel_time = [0] * (m + 1)
    congestion = [0] * (m + 1)
    u_list = [0] * (m + 1)
    v_list = [0] * (m + 1)
    
    for i in range(1, m + 1):
        u = int(next(it)); v = int(next(it)); tt = int(next(it)); cf = int(next(it))
        u_list[i] = u
        v_list[i] = v
        travel_time[i] = tt
        congestion[i] = cf
    
    q = int(next(it))
    out_lines = []
    INF = float('inf')
    
    # Prebuild static adjacency structure with edge indices to update costs quickly?
    # Let's just rebuild per query.
    adj = [[] for _ in range(n + 1)]
    # We'll rebuild adj each query using current costs.
    
    for _ in range(q):
        op = next(it)
        if op == 'UPDATE':
            road_id = int(next(it))
            new_cf = int(next(it))
            if 1 <= road_id <= m:
                congestion[road_id] = new_cf
        elif op == 'QUERY':
            s = int(next(it))
            t = int(next(it))
            # rebuild adjacency
            for i in range(1, n + 1):
                adj[i].clear()
            for i in range(1, m + 1):
                cost = travel_time[i] * congestion[i]
                adj[u_list[i]].append((v_list[i], cost))
            # Dijkstra
            if s == t:
                out_lines.append("0")
                continue
            dist = [INF] * (n + 1)
            dist[s] = 0
            pq = [(0, s)]
            while pq:
                d, node = heapq.heappop(pq)
                if d != dist[node]:
                    continue
                if node == t:
                    break
                for nei, w in adj[node]:
                    nd = d + w
                    if nd < dist[nei]:
                        dist[nei] = nd
                        heapq.heappush(pq, (nd, nei))
            if dist[t] == INF:
                out_lines.append("-1")
            else:
                out_lines.append(str(dist[t]))
    
    sys.stdout.write("\n".join(out_lines))
    if out_lines:
        sys.stdout.write("\n")

if __name__ == "__main__":
    solve()
