import sys

def longest_common_substring(s1, s2):
    m, n = len(s1), len(s2)
    if m == 0 or n == 0:
        return "-1"
    
    # Create a DP table with dimensions (m+1) x (n+1)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    max_length = 0
    ending_index = 0
    
    # Fill the DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                if dp[i][j] > max_length:
                    max_length = dp[i][j]
                    ending_index = i
            else:
                dp[i][j] = 0
    
    if max_length == 0:
        return "-1"
    
    # Extract the longest common substring
    start_index = ending_index - max_length
    return s1[start_index:ending_index]

def main():
    # Read input and split into two strings
    line = sys.stdin.readline().strip()
    if not line:
        print("-1")
        return
    
    parts = line.split()
    if len(parts) < 2:
        print("-1")
        return
    
    s1 = parts[0]
    s2 = parts[1]
    
    result = longest_common_substring(s1, s2)
    print(result)

if __name__ == "__main__":
    main()
