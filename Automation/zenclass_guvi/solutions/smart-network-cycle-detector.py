import sys
sys.setrecursionlimit(10**6)

def has_cycle_dfs(node, visited, rec_stack, adj):
    visited[node] = True
    rec_stack[node] = True
    
    for neighbor in adj[node]:
        if not visited[neighbor]:
            if has_cycle_dfs(neighbor, visited, rec_stack, adj):
                return True
        elif rec_stack[neighbor]:
            return True
    
    rec_stack[node] = False
    return False

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print("false")
        return
    
    v = int(data[0])
    e = int(data[1])
    
    if v == 0:
        print("false")
        return
    
    adj = [[] for _ in range(v)]
    index = 2
    for _ in range(e):
        u = int(data[index])
        w = int(data[index + 1])
        adj[u].append(w)
        index += 2
    
    visited = [False] * v
    rec_stack = [False] * v
    
    for i in range(v):
        if not visited[i]:
            if has_cycle_dfs(i, visited, rec_stack, adj):
                print("true")
                return
    
    print("false")

if __name__ == "__main__":
    main()
