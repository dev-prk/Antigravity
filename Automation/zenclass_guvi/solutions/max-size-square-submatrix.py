import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    idx = 0
    n = int(data[idx]); idx += 1
    m = int(data[idx]); idx += 1
    
    matrix = []
    for i in range(n):
        row = list(map(int, data[idx:idx+m]))
        idx += m
        matrix.append(row)
    
    # DP for largest square of 1s
    # dp[i][j] = size of largest square with bottom-right at (i,j)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    max_size = 0
    max_i = 0
    max_j = 0
    
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if matrix[i-1][j-1] == 1:
                dp[i][j] = min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1
                if dp[i][j] > max_size:
                    max_size = dp[i][j]
                    max_i = i
                    max_j = j
            else:
                dp[i][j] = 0
    
    if max_size == 0:
        print(0)
    else:
        # max_i is 1-indexed row of bottom-right, max_j is 1-indexed col of bottom-right
        # The square goes from row (max_i - max_size) to (max_i - 1) in 0-indexed
        # and col (max_j - max_size) to (max_j - 1) in 0-indexed
        start_row = max_i - max_size
        start_col = max_j - max_size
        end_row = max_i - 1
        end_col = max_j - 1
        
        lines = []
        for i in range(start_row, end_row + 1):
            row_vals = [str(matrix[i][j]) for j in range(start_col, end_col + 1)]
            lines.append(' '.join(row_vals))
        print('\n'.join(lines))

if __name__ == "__main__":
    main()
