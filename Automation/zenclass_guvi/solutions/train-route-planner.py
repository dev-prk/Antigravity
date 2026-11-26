import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    edges = []
    x_vals = set()
    y_vals = set()
    
    idx = 1
    for i in range(n):
        x = data[idx]
        y = data[idx + 1]
        edges.append((x, y))
        x_vals.add(x)
        y_vals.add(y)
        idx += 2
    
    # P1 is the one that appears in X but not in Y
    p1 = None
    for x in x_vals:
        if x not in y_vals:
            p1 = x
            break
    
    # Build adjacency list
    adj = {}
    for x, y in edges:
        if x not in adj:
            adj[x] = y
    
    # Trace the path
    path = []
    current = p1
    for _ in range(n):
        next_node = adj[current]
        path.append((current, next_node))
        current = next_node
    
    for s1, s2 in path:
        print(f"{s1} to {s2}")

if __name__ == "__main__":
    main()
