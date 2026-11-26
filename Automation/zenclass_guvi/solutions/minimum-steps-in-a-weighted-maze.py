import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    m = int(data[1])
    
    if n == 0 or m == 0:
        print(-1)
        return
    
    index = 2
    matrix = []
    for i in range(n):
        row = list(map(int, data[index:index + m]))
        matrix.append(row)
        index += m
    
    dp = [[0] * m for _ in range(n)]
    dp[0][0] = matrix[0][0]
    
    for i in range(n):
        for j in range(m):
            if i == 0 and j == 0:
                continue
            if i == 0:
                dp[i][j] = dp[i][j - 1] + matrix[i][j]
            elif j == 0:
                dp[i][j] = dp[i - 1][j] + matrix[i][j]
            else:
                dp[i][j] = min(dp[i - 1][j], dp[i][j - 1]) + matrix[i][j]
    
    print(dp[n - 1][m - 1])

if __name__ == "__main__":
    main()
