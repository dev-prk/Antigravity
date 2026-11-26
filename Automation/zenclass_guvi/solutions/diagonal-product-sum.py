import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    
    if n == 0:
        print(-1)
        return
    
    if len(data) < 1 + n * n:
        print(-1)
        return
    
    matrix = []
    idx = 1
    for i in range(n):
        row = list(map(int, data[idx:idx + n]))
        idx += n
        matrix.append(row)
    
    left_diag_product = 1
    right_diag_product = 1
    
    for i in range(n):
        left_diag_product *= matrix[i][i]
        right_diag_product *= matrix[i][n - 1 - i]
    
    print(left_diag_product + right_diag_product)

if __name__ == "__main__":
    main()
