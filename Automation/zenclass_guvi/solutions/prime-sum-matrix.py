import sys

def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    if n == 3:
        return True
    if n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def main():
    data = sys.stdin.read().split()
    idx = 0
    if idx >= len(data):
        return
    rows = int(data[idx]); idx += 1
    cols = int(data[idx]); idx += 1
    
    matrix = []
    for r in range(rows):
        row = []
        for c in range(cols):
            if idx < len(data):
                row.append(int(data[idx])); idx += 1
            else:
                row.append(0)
        matrix.append(row)
    
    total_sum = 0
    for i in range(rows):
        for j in range(cols):
            if is_prime(i + j):
                total_sum += matrix[i][j]
    
    print("YES" if is_prime(total_sum) else "NO")

if __name__ == "__main__":
    main()
