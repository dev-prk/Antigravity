import sys
from collections import deque

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    
    if n == 0:
        print(0)
        return
    
    matrix = []
    index = 1
    for i in range(n):
        row = list(map(int, data[index:index + n]))
        matrix.append(row)
        index += n
    
    if n == 1:
        print(1 if matrix[0][0] == 1 else 0)
        return
    
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    count = 0
    
    for i in range(n):
        for j in range(n):
            if matrix[i][j] == 1:
                is_island = True
                for dx, dy in directions:
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < n and 0 <= nj < n and matrix[ni][nj] == 1:
                        is_island = False
                        break
                if is_island:
                    count += 1
    
    print(count)

if __name__ == "__main__":
    main()
