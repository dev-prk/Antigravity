import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    m = int(data[1])
    
    edges = []
    index = 2
    for i in range(m):
        u = int(data[index])
        v = int(data[index + 1])
        w = int(data[index + 2])
        index += 3
        edges.append((w, u, v))
    
    # Sort edges by weight
    edges.sort()
    
    # Union-Find with path compression and union by rank
    parent = list(range(n))
    rank = [0] * n
    
    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    
    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry:
            return False
        if rank[rx] < rank[ry]:
            parent[rx] = ry
        elif rank[rx] > rank[ry]:
            parent[ry] = rx
        else:
            parent[ry] = rx
            rank[rx] += 1
        return True
    
    total_cost = 0
    
    for w, u, v in edges:
        if union(u, v):
            total_cost += w
    
    print(total_cost)

if __name__ == "__main__":
    main()
