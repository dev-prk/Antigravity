import sys
sys.setrecursionlimit(2000000)

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    
    if n == 0:
        print(-1)
        return
    
    matrix = []
    index = 1
    
    for i in range(n):
        if index >= len(data):
            print(-1)
            return
        row = list(map(int, data[index:index + n]))
        if len(row) < n:
            print(-1)
            return
        matrix.append(row)
        index += n
    
    def count_isolated_ones(grid, size):
        count = 0
        for i in range(size):
            for j in range(size):
                if grid[i][j] == 1:
                    is_isolated = True
                    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                    for dx, dy in directions:
                        ni, nj = i + dx, j + dy
                        if 0 <= ni < size and 0 <= nj < size:
                            if grid[ni][nj] == 1:
                                is_isolated = False
                                break
                    if is_isolated:
                        count += 1
        return count
    
    result = count_isolated_ones(matrix, n)
    
    if result == 0:
        print(-1)
    else:
        print(result)

if __name__ == "__main__":
    main()
