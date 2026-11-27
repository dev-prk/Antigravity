import sys
sys.setrecursionlimit(200000)

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print("no")
        return
    
    n = int(data[0])
    m = int(data[1])
    
    if n <= 0 or m < 0:
        print("no")
        return
    
    adj = [[] for _ in range(n + 1)]
    
    idx = 2
    for _ in range(m):
        if idx + 1 >= len(data):
            break
        u = int(data[idx])
        v = int(data[idx + 1])
        idx += 2
        
        if 1 <= u <= n and 1 <= v <= n:
            adj[u].append(v)
    
    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * (n + 1)
    has_cycle = [False]
    
    def dfs(node):
        if has_cycle[0]:
            return
        color[node] = GRAY
        for neighbor in adj[node]:
            if color[neighbor] == GRAY:
                has_cycle[0] = True
                return
            if color[neighbor] == WHITE:
                dfs(neighbor)
        color[node] = BLACK
    
    for i in range(1, n + 1):
        if color[i] == WHITE:
            dfs(i)
            if has_cycle[0]:
                break
    
    print("yes" if has_cycle[0] else "no")

if __name__ == "__main__":
    main()
