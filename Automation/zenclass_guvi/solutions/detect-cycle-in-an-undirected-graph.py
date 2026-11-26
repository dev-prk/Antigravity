import sys
sys.setrecursionlimit(200000)

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print("No Cycle")
        return
    
    n = int(data[0])
    m = int(data[1])
    
    if m <= 1:
        print("No Cycle")
        return
    
    adj = [[] for _ in range(n + 1)]
    index = 2
    for _ in range(m):
        u = int(data[index])
        v = int(data[index + 1])
        index += 2
        adj[u].append(v)
        adj[v].append(u)
    
    visited = [False] * (n + 1)
    parent = [0] * (n + 1)
    
    for start in range(1, n + 1):
        if visited[start]:
            continue
        
        stack = [(start, 0)]
        
        while stack:
            node, par = stack.pop()
            
            if visited[node]:
                continue
            
            visited[node] = True
            parent[node] = par
            
            for neighbor in adj[node]:
                if not visited[neighbor]:
                    stack.append((neighbor, node))
                elif neighbor != par:
                    print("Cycle Detected")
                    return
    
    print("No Cycle")

if __name__ == "__main__":
    main()
