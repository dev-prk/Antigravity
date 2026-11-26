import sys
from collections import defaultdict

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    points = []
    idx = 1
    for i in range(n):
        x = int(data[idx])
        y = int(data[idx + 1])
        points.append((x, y))
        idx += 2
    
    if n <= 1:
        print(0)
        return
    
    rows = defaultdict(list)
    cols = defaultdict(list)
    
    for x, y in points:
        rows[y].append(x)
        cols[x].append(y)
    
    for y in rows:
        rows[y].sort()
    for x in cols:
        cols[x].sort()
    
    parent = list(range(n))
    rank = [0] * n
    
    def find(u):
        if parent[u] != u:
            parent[u] = find(parent[u])
        return parent[u]
    
    def union(u, v):
        pu = find(u)
        pv = find(v)
        if pu == pv:
            return
        if rank[pu] < rank[pv]:
            pu, pv = pv, pu
        parent[pv] = pu
        if rank[pu] == rank[pv]:
            rank[pu] += 1
    
    point_to_idx = {pt: i for i, pt in enumerate(points)}
    
    for y, xs in rows.items():
        for i in range(len(xs) - 1):
            x1, x2 = xs[i], xs[i + 1]
            for x in range(x1 + 1, x2):
                p1 = (x1, y)
                p2 = (x, y)
                p3 = (x2, y)
                if p1 in point_to_idx and p3 in point_to_idx:
                    union(point_to_idx[p1], point_to_idx[p3])
    
    for x, ys in cols.items():
        for i in range(len(ys) - 1):
            y1, y2 = ys[i], ys[i + 1]
            for y in range(y1 + 1, y2):
                p1 = (x, y1)
                p2 = (x, y)
                p3 = (x, y2)
                if p1 in point_to_idx and p3 in point_to_idx:
                    union(point_to_idx[p1], point_to_idx[p3])
    
    components = set()
    for i in range(n):
        components.add(find(i))
    
    print(len(components) - 1)

if __name__ == "__main__":
    main()
