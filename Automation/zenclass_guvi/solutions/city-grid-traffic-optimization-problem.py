import sys

def solve() -> None:
    lines = sys.stdin.read().strip().splitlines()
    if not lines:
        print(-1)
        return
    
    parts = lines[0].strip().split()
    if len(parts) < 2:
        print(-1)
        return
    
    try:
        m = int(parts[0])
        n = int(parts[1])
    except ValueError:
        print(-1)
        return
    
    if m <= 0 or n <= 0:
        print(-1)
        return
    
    if len(lines) - 1 < m:
        print(-1)
        return
    
    grid = []
    for i in range(m):
        row_parts = lines[1 + i].strip().split()
        if len(row_parts) != n:
            print(-1)
            return
        try:
            row = [int(x) for x in row_parts]
        except ValueError:
            print(-1)
            return
        grid.append(row)
    
    dp = [0] * n
    for i in range(m):
        for j in range(n):
            val = grid[i][j]
            if i == 0 and j == 0:
                dp[j] = val
            elif i == 0:
                dp[j] = dp[j - 1] + val
            elif j == 0:
                dp[j] = dp[j] + val
            else:
                dp[j] = min(dp[j], dp[j - 1]) + val
    print(dp[-1])

if __name__ == "__main__":
    solve()
