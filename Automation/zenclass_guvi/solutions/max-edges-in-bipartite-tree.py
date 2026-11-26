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
    
    for _ in range(n - 1):
        u = int(data[index])
        v = int(data[index + 1])
        index += 2
        adj[u].append(v)
        adj[v].append(u)
    
    color = [-1] * (n + 1)
    color[1] = 0
    q = deque([1])
    
    while q:
        node = q.popleft()
        for neighbor in adj[node]:
            if color[neighbor] == -1:
                color[neighbor] = 1 - color[node]
                q.append(neighbor)
    
    cnt0 = sum(1 for i in range(1, n + 1) if color[i] == 0)
    cnt1 = n - cnt0
    
    max_edges = (cnt0 * cnt1) - (n - 1)
    print(max_edges)

if __name__ == "__main__":
    main()
