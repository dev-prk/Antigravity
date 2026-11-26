import sys
from collections import deque

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print("no")
        return
    
    n = int(data[0])
    m = int(data[1])
    
    if n == 0 or m == 0:
        print("no")
        return
    
    matrix = []
    idx = 2
    for i in range(n):
        row = list(map(int, data[idx:idx+m]))
        matrix.append(row)
        idx += m
    
    if matrix[0][0] == 0 or matrix[n-1][m-1] == 0:
        print("no")
        return
    
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),           (0, 1),
                  (1, -1),  (1, 0),  (1, 1)]
    
    visited = [[False] * m for _ in range(n)]
    queue = deque([(0, 0)])
    visited[0][0] = True
    
    while queue:
        x, y = queue.popleft()
        
        if x == n - 1 and y == m - 1:
            print("yes")
            return
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < n and 0 <= ny < m:
                if not visited[nx][ny] and matrix[nx][ny] == 1:
                    visited[nx][ny] = True
                    queue.append((nx, ny))
    
    print("no")

if __name__ == "__main__":
    main()
