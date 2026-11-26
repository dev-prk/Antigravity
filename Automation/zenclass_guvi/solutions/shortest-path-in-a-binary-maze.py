from collections import deque
import sys

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    m = int(data[1])
    
    matrix = []
    index = 2
    for i in range(n):
        row = list(map(int, data[index:index + m]))
        matrix.append(row)
        index += m
    
    # Check if start or end is blocked
    if matrix[0][0] == 0 or matrix[n-1][m-1] == 0:
        print(-1)
        return
    
    # Special case: start is end
    if n == 1 and m == 1:
        print(0)
        return
    
    # BFS
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    visited = [[False] * m for _ in range(n)]
    queue = deque([(0, 0, 0)])  # (row, col, steps)
    visited[0][0] = True
    
    while queue:
        row, col, steps = queue.popleft()
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            
            if 0 <= new_row < n and 0 <= new_col < m:
                if not visited[new_row][new_col] and matrix[new_row][new_col] == 1:
                    if new_row == n - 1 and new_col == m - 1:
                        print(steps + 1)
                        return
                    visited[new_row][new_col] = True
                    queue.append((new_row, new_col, steps + 1))
    
    print(-1)

if __name__ == "__main__":
    solve()
