import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    m = int(data[1])
    
    if n == 0 or m == 0:
        print(0)
        return
    
    values = list(map(int, data[2:2 + n * m]))
    
    grid = []
    for i in range(n):
        row = values[i * m:(i + 1) * m]
        grid.append(row)
    
    dp = [[0] * m for _ in range(n)]
    dp[0][0] = grid[0][0]
    
    for i in range(n):
        for j in range(m):
            if i == 0 and j == 0:
                continue
            from_top = dp[i - 1][j] if i > 0 else -1
            from_left = dp[i][j - 1] if j > 0 else -1
            max_prev = max(from_top, from_left)
            dp[i][j] = max_prev + grid[i][j]
    
    print(dp[n - 1][m - 1])

if __name__ == "__main__":
    main()
