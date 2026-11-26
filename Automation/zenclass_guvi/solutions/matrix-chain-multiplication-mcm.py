import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    
    if n == 0:
        print(0)
        return
    
    arr = list(map(int, data[1:1+n+1]))
    
    # dp[i][j] = minimum cost to multiply matrices from i to j
    # We have n matrices, indexed 0 to n-1
    # arr has size n+1
    
    dp = [[0] * n for _ in range(n)]
    
    # chain length from 2 to n
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = float('inf')
            for k in range(i, j):
                # cost = dp[i][k] + dp[k+1][j] + arr[i] * arr[k+1] * arr[j+1]
                cost = dp[i][k] + dp[k+1][j] + arr[i] * arr[k+1] * arr[j+1]
                dp[i][j] = min(dp[i][j], cost)
    
    print(dp[0][n-1])

if __name__ == "__main__":
    main()
