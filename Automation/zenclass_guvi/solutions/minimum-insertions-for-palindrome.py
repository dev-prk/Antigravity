import sys

def min_insertions_for_palindrome(s):
    n = len(s)
    if n <= 1:
        return 0
    
    # Create a table to store LPS lengths
    # lps[i][j] = length of longest palindromic subsequence in s[i:j+1]
    dp = [[0] * n for _ in range(n)]
    
    # Strings of length 1 are palindromes of length 1
    for i in range(n):
        dp[i][i] = 1
    
    # Fill the table for substrings of length 2 to n
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j]:
                dp[i][j] = dp[i + 1][j - 1] + 2
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])
    
    # Minimum insertions = length of string - length of LPS
    return n - dp[0][n - 1]

def main():
    s = sys.stdin.readline().strip()
    result = min_insertions_for_palindrome(s)
    print(result)

if __name__ == "__main__":
    main()
