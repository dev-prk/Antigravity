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
    
    matrix = []
    idx = 2
    for i in range(n):
        row = list(map(int, data[idx:idx + m]))
        matrix.append(row)
        idx += m
    
    result = []
    
    # Collect elements in order:
    # 1. Primary diagonal (top-left to bottom-right)
    for i in range(min(n, m)):
        result.append(matrix[i][i])
    
    # 2. Anti-diagonal (top-right to bottom-left), excluding center if already included
    for i in range(min(n, m)):
        j = m - 1 - i
        if i != j:  # Avoid duplicate center in odd-sized matrices
            result.append(matrix[i][j])
    
    if not result:
        print(-1)
    else:
        print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
