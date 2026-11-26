import sys
from collections import defaultdict

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print('no')
        return
    
    n = int(data[0])
    e = int(data[1])
    
    # Edge case: 0 nodes
    if n == 0:
        print('yes')
        return
    
    # Edge case: 1 node, 0 edges
    if n == 1 and e == 0:
        print('yes')
        return
    
    # Edge case: no edges but more than 1 node
    if e == 0:
        print('no')
        return
    
    edges = data[2:]
    
    # Build adjacency list and count children
    children_count = defaultdict(int)
    adj = defaultdict(list)
    
    for i in range(e):
        parent = int(edges[2*i])
        child = int(edges[2*i + 1])
        adj[parent].append(child)
        children_count[child] += 1
    
    # Check if any node has more than 2 children
    for parent in adj:
        if len(adj[parent]) > 2:
            print('no')
            return
    
    # Check if any node has more than 1 parent (degree > 1)
    for child in children_count:
        if children_count[child] > 1:
            print('no')
            return
    
    # Find root (node with no parents)
    all_nodes = set()
    for parent, child in zip(edges[0::2], edges[1::2]):
        all_nodes.add(int(parent))
        all_nodes.add(int(child))
    
    root = None
    for node in all_nodes:
        if children_count.get(node, 0) == 0:
            root = node
            break
    
    if root is None:
        print('no')
        return
    
    # BFS to check connectivity and count all nodes
    visited = set()
    queue = [root]
    visited.add(root)
    node_count = 1
    
    while queue:
        node = queue.pop(0)
        for child in adj[node]:
            if child in visited:
                print('no')
                return
            visited.add(child)
            queue.append(child)
            node_count += 1
    
    # Check if we visited exactly n nodes and all edges were used
    if node_count == n and len(visited) == n:
        print('yes')
    else:
        print('no')

if __name__ == "__main__":
    main()
