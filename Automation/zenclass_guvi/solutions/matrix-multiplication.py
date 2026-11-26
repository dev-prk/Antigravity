import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    idx = 0
    rows_a = int(data[idx])
    cols_a = int(data[idx + 1])
    idx += 2
    
    matrix_a = []
    for _ in range(rows_a):
        row = list(map(int, data[idx:idx + cols_a]))
        matrix_a.append(row)
        idx += cols_a
    
    rows_b = int(data[idx])
    cols_b = int(data[idx + 1])
    idx += 2
    
    matrix_b = []
    for _ in range(rows_b):
        row = list(map(int, data[idx:idx + cols_b]))
        matrix_b.append(row)
        idx += cols_b
    
    result = [[0] * cols_b for _ in range(rows_a)]
    
    for i in range(rows_a):
        for j in range(cols_b):
            for k in range(cols_a):
                result[i][j] += matrix_a[i][k] * matrix_b[k][j]
    
    for row in result:
        print(' '.join(map(str, row)))

if __name__ == "__main__":
    main()
