import sys

def longest_palindrome_removal(s):
    n = len(s)
    if n == 0:
        return 0
    
    # dp[i][j] = True if s[i:j+1] is a palindrome
    is_pal = [[False] * n for _ in range(n)]
    
    # Fill the dp table for palindromes
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            if i == j:
                is_pal[i][j] = True
            elif j == i + 1:
                is_pal[i][j] = (s[i] == s[j])
            else:
                is_pal[i][j] = (s[i] == s[j] and is_pal[i + 1][j - 1])
    
    # dp2[i] = length of longest palindrome starting at index i
    dp_end = [0] * n
    
    for i in range(n - 1, -1, -1):
        dp_end[i] = 1  # At least the single character
        for j in range(i, n):
            if is_pal[i][j]:
                length = j - i + 1
                if length > dp_end[i]:
                    dp_end[i] = length
                # If we can extend from the right
                if j + 1 < n:
                    dp_end[i] = max(dp_end[i], dp_end[j + 1] + length)
    
    # dp[i] = minimum remaining length after removing palindromes from s[i:]
    dp_start = [float('inf')] * (n + 1)
    dp_start[n] = 0  # Empty string has 0 remaining
    
    for i in range(n - 1, -1, -1):
        # Option 1: remove single character
        dp_start[i] = min(dp_start[i], 1 + dp_start[i + 1])
        
        # Option 2: remove a palindrome starting at i
        for j in range(i, n):
            if is_pal[i][j]:
                length = j - i + 1
                # Remove s[i:j+1], then continue from s[j+1:]
                dp_start[i] = min(dp_start[i], dp_start[j + 1])
    
    return dp_start[0]

def main():
    s = sys.stdin.readline().strip()
    result = longest_palindrome_removal(s)
    print(result)

if __name__ == "__main__":
    main()
