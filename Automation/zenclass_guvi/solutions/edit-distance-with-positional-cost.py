import sys

def pos(c):
    return ord(c) - ord('a') + 1

def solve():
    line = sys.stdin.readline()
    if not line:
        return
    parts = line.rstrip('\n').split()
    if len(parts) < 2:
        return
    A, B = parts[0], parts[1]
    
    m, n = len(A), len(B)
    
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        dp[i][0] = 0
    for j in range(n + 1):
        dp[0][j] = 0
    
    for i in range(1, m + 1):
        dp[i][0] = dp[i-1][0] + pos(A[i-1])
    
    for j in range(1, n + 1):
        dp[0][j] = dp[0][j-1] + pos(B[j-1])
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            delete_cost = dp[i-1][j] + pos(A[i-1])
            insert_cost = dp[i][j-1] + pos(B[j-1])
            substitute_cost = dp[i-1][j-1] + abs(pos(A[i-1]) - pos(B[j-1]))
            dp[i][j] = min(delete_cost, insert_cost, substitute_cost)
    
    print(dp[m][n])

if __name__ == "__main__":
    solve()
