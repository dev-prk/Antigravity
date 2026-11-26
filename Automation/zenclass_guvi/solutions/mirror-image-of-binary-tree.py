import sys
from collections import deque

def main():
    sys.setrecursionlimit(1 << 25)
    n = int(sys.stdin.readline().strip())
    if n == 0:
        return
    if n == 1:
        print(1)
        return
    
    children = {}
    parent = {}
    for _ in range(n - 1):
        parts = sys.stdin.readline().split()
        u, v = int(parts[0]), int(parts[1])
        if u not in children:
            children[u] = []
        children[u].append(v)
        parent[v] = u
        if v not in children:
            children[v] = []
    
    root = 1
    
    # Build the mirror tree structure
    # For each node, we need to swap left and right children
    mirror_children = {}
    def build_mirror(node):
        if node not in children:
            mirror_children[node] = []
            return []
        kids = children[node][::-1]  # Reverse the order for mirror
        mirror_children[node] = kids
        for kid in kids:
            build_mirror(kid)
    
    build_mirror(root)
    
    # BFS to output edges in the correct order
    result = []
    queue = deque([root])
    while queue:
        u = queue.popleft()
        if u in mirror_children:
            for v in mirror_children[u]:
                result.append((u, v))
                queue.append(v)
    
    for u, v in result:
        print(u, v)

if __name__ == "__main__":
    main()
