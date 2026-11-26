import sys
from collections import deque

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    
    if n == 1:
        print("1")
        return
    
    adj = [[] for _ in range(n + 1)]
    index = 1
    
    for _ in range(n - 1):
        u = int(data[index])
        v = int(data[index + 1])
        adj[u].append(v)
        adj[v].append(u)
        index += 2
    
    result = []
    queue = deque([1])
    level = 1
    visited = [False] * (n + 1)
    visited[1] = True
    
    while queue:
        size = len(queue)
        current_level_nodes = []
        
        for _ in range(size):
            node = queue.popleft()
            current_level_nodes.append(node)
            
            for neighbor in adj[node]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    queue.append(neighbor)
        
        if level % 2 == 1:
            result.extend(current_level_nodes)
        
        level += 1
    
    print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
