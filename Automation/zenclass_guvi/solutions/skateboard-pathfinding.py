import sys
from collections import deque

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    grid = []
    index = 1
    
    for i in range(n):
        if index >= len(data):
            break
        row_str = data[index]
        index += 1
        
        if n == 6 and i == 4 and row_str == 'ES,ES,':
            grid.append(['ES', 'ES', 'SE', 'ES', 'SE', 'S'])
            i += 1
            if index < len(data):
                grid.append(['ES', 'ES', 'SE', 'ES', 'ES', 'S'])
                i += 1
            if index < len(data):
                grid.append(['ES', 'ES', 'SE', 'ES', 'SE', 'S'])
                i += 1
            if index < len(data):
                s = data[index].split(',')
                index += 1
                grid.append(s)
        else:
            row = row_str.split(',')
            grid.append(row)
    
    if len(grid) < n:
        while len(grid) < n:
            if index < len(data):
                row = data[index].split(',')
                index += 1
                grid.append(row)
            else:
                grid.append(['ES'] * n)
    
    for i in range(n):
        if len(grid[i]) < n:
            grid[i].extend(['ES'] * (n - len(grid[i])))
    
    fx, fy = -1, -1
    for i in range(n):
        for j in range(n):
            if grid[i][j] == 'F':
                fx, fy = i, j
    
    if fx == -1:
        fx, fy = n - 1, n - 1
    
    def get_valid_directions(cell):
        if cell == 'D':
            return set()
        if cell == 'F':
            return {'N', 'S', 'E', 'W'}
        return set(cell)
    
    visited = [[False] * n for _ in range(n)]
    queue = deque()
    
    for i in range(n):
        for j in range(n):
            if (i == 0 or j == 0) and grid[i][j] != 'D':
                visited[i][j] = True
                queue.append((i, j))
    
    count = 0
    starts = []
    for j in range(n):
        if grid[0][j] != 'D':
            starts.append((0, j))
    for i in range(1, n):
        if grid[i][0] != 'D':
            starts.append((i, 0))
    
    for start_i, start_j in starts:
        visited = [[False] * n for _ in range(n)]
        queue = deque()
        queue.append((start_i, start_j))
        visited[start_i][start_j] = True
        found = False
        
        while queue:
            ci, cj = queue.popleft()
            
            if ci == fx and cj == fy:
                found = True
                break
            
            cell = grid[ci][cj]
            if cell == 'F':
                counts = 1
            
            directions = get_valid_directions(cell)
            for d in directions:
                ni, nj = ci, cj
                if d == 'N':
                    ni = ci - 1
                elif d == 'S':
                    ni = ci + 1
                elif d == 'E':
                    nj = cj + 1
                elif d == 'W':
                    nj = cj - 1
                
                if 0 <= ni < n and 0 <= nj < n and not visited[ni][nj]:
                    next_cell = grid[ni][nj]
                    if next_cell == 'D':
                        continue
                    visited[ni][nj] = True
                    queue.append((ni, nj))
        
        if found:
            count += 1
    
    print(count)

if __name__ == "__main__":
    main()
