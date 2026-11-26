import sys
sys.setrecursionlimit(300000)

MOD = 1000000007

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    
    it = iter(data)
    n = int(next(it))
    cost = [int(next(it)) for _ in range(n)]
    m = int(next(it))
    
    graph = [[] for _ in range(n)]
    for _ in range(m):
        u = int(next(it)) - 1
        v = int(next(it)) - 1
        graph[u].append(v)
    
    # Use iterative Tarjan's algorithm to avoid recursion depth issues
    index_counter = [0]
    indices = [-1] * n
    lowlink = [-1] * n
    on_stack = [False] * n
    stack = []
    sccs = []
    
    def strongconnect(v):
        # Iterative version of Tarjan's SCC
        work_stack = [(v, 0)]  # (node, next_child_index)
        while work_stack:
            node, next_idx = work_stack[-1]
            if indices[node] == -1:
                indices[node] = lowlink[node] = index_counter[0]
                index_counter[0] += 1
                stack.append(node)
                on_stack[node] = True
            
            if next_idx < len(graph[node]):
                neighbor = graph[node][next_idx]
                work_stack[-1] = (node, next_idx + 1)
                if indices[neighbor] == -1:
                    work_stack.append((neighbor, 0))
                elif on_stack[neighbor]:
                    lowlink[node] = min(lowlink[node], indices[neighbor])
            else:
                work_stack.pop()
                if work_stack:
                    parent = work_stack[-1][0]
                    lowlink[parent] = min(lowlink[parent], lowlink[node])
                
                if lowlink[node] == indices[node]:
                    scc = []
                    while True:
                        w = stack.pop()
                        on_stack[w] = False
                        scc.append(w)
                        if w == node:
                            break
                    sccs.append(scc)
    
    for v in range(n):
        if indices[v] == -1:
            strongconnect(v)
    
    total_cost = 0
    ways = 1
    
    for scc in sccs:
        min_c = min(cost[i] for i in scc)
        total_cost += min_c
        count_min = sum(1 for i in scc if cost[i] == min_c)
        ways = (ways * count_min) % MOD
    
    print(total_cost, ways)

if __name__ == "__main__":
    main()
