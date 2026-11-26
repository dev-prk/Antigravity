import sys

def main():
    MOD = 1000000007
    
    line = sys.stdin.readline()
    if not line:
        print(0)
        return
    
    parts = line.split()
    if len(parts) < 2:
        print(0)
        return
    
    N = int(parts[0])
    M = int(parts[1])
    
    if N == 0 or M == 0:
        print(0)
        return
    
    grid = []
    for _ in range(N):
        line = sys.stdin.readline()
        if not line:
            print(0)
            return
        row = list(map(int, line.split()))
        if len(row) < M:
            row.extend([0] * (M - len(row)))
        grid.append(row[:M])
    
    # Check if start or end is blocked
    if grid[0][0] == 1 or grid[N-1][M-1] == 1:
        print(0)
        return
    
    # DP table
    dp = [[0] * M for _ in range(N)]
    dp[0][0] = 1
    
    for i in range(N):
        for j in range(M):
            if grid[i][j] == 1:
                dp[i][j] = 0
                continue
            
            if i == 0 and j == 0:
                continue
            
            from_top = dp[i-1][j] if i > 0 else 0
            from_left = dp[i][j-1] if j > 0 else 0
            dp[i][j] = (from_top + from_left) % MOD
    
    print(dp[N-1][M-1] % MOD)

if __name__ == "__main__":
    main()
