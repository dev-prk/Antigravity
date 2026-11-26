import sys
from collections import deque

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print("no")
        return
    
    idx = 0
    rows = int(data[idx])
    cols = int(data[idx + 1])
    idx += 2
    
    matrix = []
    for r in range(rows):
        row = list(map(int, data[idx:idx + cols]))
        matrix.append(row)
        idx += cols
    
    startRow = int(data[idx])
    startCol = int(data[idx + 1])
    
    total_cells = rows * cols
    target = total_cells - 1
    start = startRow * cols + startCol
    
    if start == target:
        print("yes")
        return
    
    visited = [False] * total_cells
    queue = deque([start])
    visited[start] = True
    
    while queue:
        curr = queue.popleft()
        curr_row = curr // cols
        curr_col = curr % cols
        curr_val = matrix[curr_row][curr_col]
        
        next_col = curr_col + 1
        next_row = curr_row
        
        if next_col >= cols:
            next_row += 1
            next_col = 0
        
        if next_row >= rows:
            continue
        
        next_val = matrix[next_row][next_col]
        
        if next_val > curr_val:
            next_idx = next_row * cols + next_col
            if not visited[next_idx]:
                if next_idx == target:
                    print("yes")
                    return
                visited[next_idx] = True
                queue.append(next_idx)
    
    print("no")

if __name__ == "__main__":
    main()
