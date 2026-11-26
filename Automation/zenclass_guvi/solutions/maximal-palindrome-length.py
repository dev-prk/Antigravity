import sys

def main():
    s = sys.stdin.readline().strip()
    n = len(s)
    if n == 0:
        print(0)
        return
    
    # dp[i][j] = length of longest palindromic nesting in s[i:j+1]
    dp = [[0] * n for _ in range(n)]
    
    # Base case: single characters
    for i in range(n):
        dp[i][i] = 1
    
    # Fill the table for substrings of increasing length
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            # Option 1: don't use s[i] and s[j]
            dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])
            # Option 2: use s[i] and s[j] if they match
            if s[i] == s[j]:
                if length == 2:
                    dp[i][j] = max(dp[i][j], 2)
                else:
                    dp[i][j] = max(dp[i][j], 2 + dp[i + 1][j - 1])
    
    print(dp[0][n - 1])

if __name__ == "__main__":
    main()
