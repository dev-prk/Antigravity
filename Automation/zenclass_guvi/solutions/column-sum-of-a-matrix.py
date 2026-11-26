import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    m = int(data[1])
    
    if n == 0 or m == 0:
        print()
        return
    
    numbers = list(map(int, data[2:2 + n * m]))
    
    col_sums = [0] * m
    for i in range(n):
        for j in range(m):
            col_sums[j] += numbers[i * m + j]
    
    print(' '.join(map(str, col_sums)))

if __name__ == "__main__":
    main()
