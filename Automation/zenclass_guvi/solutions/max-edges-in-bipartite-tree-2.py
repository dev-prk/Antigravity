import sys
from collections import deque

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    
    if n <= 1:
        print(0)
        return
    
    adj = [[] for _ in range(n + 1)]
    index = 1
    
    for i in range(n - 1):
        u = int(data[index])
        v = int(data[index + 1])
        index += 2
        adj[u].append(v)
        adj[v].append(u)
    
    color = [-1] * (n + 1)
    color[1] = 0
    q = deque([1])
    left = 0
    right = 0
    
    while q:
        node = q.popleft()
        if color[node] == 0:
            left += 1
        else:
            right += 1
        
        for neighbor in adj[node]:
            if color[neighbor] == -1:
                color[neighbor] = 1 - color[node]
                q.append(neighbor)
    
    total_possible = left * right
    existing_edges = n - 1
    max_new_edges = total_possible - existing_edges
    
    print(max_new_edges)

if __name__ == "__main__":
    main()
