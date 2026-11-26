import sys

def lcs_of_three(s1, s2, s3):
    m, n, p = len(s1), len(s2), len(s3)
    
    # Create a 3D DP table
    dp = [[[0] * (p + 1) for _ in range(n + 1)] for _ in range(m + 1)]
    
    # Fill the DP table
    for i in range(m + 1):
        for j in range(n + 1):
            for k in range(p + 1):
                if i == 0 or j == 0 or k == 0:
                    dp[i][j][k] = 0
                elif s1[i-1] == s2[j-1] == s3[k-1]:
                    dp[i][j][k] = dp[i-1][j-1][k-1] + 1
                else:
                    dp[i][j][k] = max(dp[i-1][j][k], dp[i][j-1][k], dp[i][j][k-1])
    
    # If no common subsequence exists
    if dp[m][n][p] == 0:
        return "-1"
    
    # Backtrack to find the LCS
    result = []
    i, j, k = m, n, p
    while i > 0 and j > 0 and k > 0:
        if s1[i-1] == s2[j-1] == s3[k-1]:
            result.append(s1[i-1])
            i -= 1
            j -= 1
            k -= 1
        else:
            # Move in the direction of maximum value
            if dp[i-1][j][k] >= dp[i][j-1][k] and dp[i-1][j][k] >= dp[i][j][k-1]:
                i -= 1
            elif dp[i][j-1][k] >= dp[i][j][k-1]:
                j -= 1
            else:
                k -= 1
    
    # Reverse to get the correct order
    result.reverse()
    return ''.join(result)

def main():
    # Read input
    line = sys.stdin.readline().strip()
    if not line:
        print(-1)
        return
    
    strings = line.split()
    if len(strings) != 3:
        print(-1)
        return
    
    s1, s2, s3 = strings[0], strings[1], strings[2]
    
    # Find and print LCS of three strings
    result = lcs_of_three(s1, s2, s3)
    print(result)

if __name__ == "__main__":
    main()
