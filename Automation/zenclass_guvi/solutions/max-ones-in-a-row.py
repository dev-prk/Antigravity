import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    m = int(data[1])
    
    if n == 0 or m == 0:
        print(0)
        return
    
    if len(data) < 2 + n * m:
        print(-1)
        return
    
    matrix_values = list(map(int, data[2:2 + n * m]))
    
    max_ones = 0
    for i in range(n):
        row_start = i * m
        row_end = (i + 1) * m
        row = matrix_values[row_start:row_end]
        current_ones = sum(row)
        if current_ones > max_ones:
            max_ones = current_ones
    
    print(max_ones)

if __name__ == "__main__":
    main()
