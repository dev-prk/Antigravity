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
    
    idx = 2
    matrix = []
    for i in range(n):
        row = list(map(int, data[idx:idx + m]))
        matrix.append(row)
        idx += m
    
    # Calculate column sums
    col_sums = [0] * m
    for j in range(m):
        for i in range(n):
            col_sums[j] += matrix[i][j]
    
    # Find columns where sum is divisible by 3
    valid_cols = [j for j in range(m) if col_sums[j] % 3 == 0]
    
    if not valid_cols:
        print(-1)
        return
    
    # Print each valid column as a row
    for j in valid_cols:
        col = [matrix[i][j] for i in range(n)]
        print(' '.join(map(str, col)))

if __name__ == "__main__":
    main()
