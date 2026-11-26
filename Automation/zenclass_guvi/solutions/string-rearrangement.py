import sys
from collections import defaultdict

def can_rearrange(s):
    words = s.split()
    if not words:
        return 1
    
    in_degree = defaultdict(int)
    out_degree = defaultdict(int)
    graph = defaultdict(set)
    vertices = set()
    
    for word in words:
        if len(word) == 0:
            continue
        start = word[0]
        end = word[-1]
        out_degree[start] += 1
        in_degree[end] += 1
        graph[start].add(end)
        vertices.add(start)
        vertices.add(end)
    
    # Check Eulerian path conditions
    start_count = 0
    end_count = 0
    
    for v in vertices:
        diff = out_degree[v] - in_degree[v]
        if diff == 1:
            start_count += 1
        elif diff == -1:
            end_count += 1
        elif diff != 0:
            return 0
    
    if start_count > 1 or end_count > 1:
        return 0
    
    # Check connectivity using BFS
    non_isolated = [v for v in vertices if in_degree[v] > 0 or out_degree[v] > 0]
    if not non_isolated:
        return 1
    
    visited = set()
    queue = [non_isolated[0]]
    visited.add(non_isolated[0])
    
    while queue:
        node = queue.pop(0)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
        # Also check reverse edges
        for v in vertices:
            if node in graph[v] and v not in visited:
                visited.add(v)
                queue.append(v)
    
    for v in non_isolated:
        if v not in visited:
            return 0
    
    return 1

s = sys.stdin.read().strip()
result = can_rearrange(s)
sys.stdout.write(str(result))
