import sys

def longest_common_subarray(s1, s2):
    n, m = len(s1), len(s2)
    if n == 0 or m == 0:
        return ""
    
    max_len = 0
    end_idx = -1
    
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                if dp[i][j] >= max_len:
                    max_len = dp[i][j]
                    end_idx = i - 1
    
    if max_len == 0:
        return ""
    
    return s1[end_idx - max_len + 1:end_idx + 1]

def main():
    lines = sys.stdin.read().splitlines()
    if len(lines) < 2:
        return
    
    s1 = lines[0].strip()
    s2 = lines[1].strip()
    
    result = longest_common_subarray(s1, s2)
    print(result)

if __name__ == "__main__":
    main()
