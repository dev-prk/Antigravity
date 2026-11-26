import sys

def min_edit_distance(X, Y):
    m, n = len(X), len(Y)
    # Create a 2D DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Initialize base cases
    for i in range(m + 1):
        dp[i][0] = i  # Deleting all characters from X[0:i]
    for j in range(n + 1):
        dp[0][j] = j  # Inserting all characters of Y[0:j]
    
    # Fill the DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if X[i-1] == Y[j-1]:
                dp[i][j] = dp[i-1][j-1]  # No operation needed
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],    # Delete
                    dp[i][j-1],    # Insert
                    dp[i-1][j-1]   # Replace
                )
    
    return dp[m][n]

def main():
    line = sys.stdin.readline().strip()
    if not line:
        return
    parts = line.split()
    if len(parts) >= 2:
        X = parts[0].strip()
        Y = parts[1].strip()
        result = min_edit_distance(X, Y)
        print(result)

if __name__ == "__main__":
    main()
