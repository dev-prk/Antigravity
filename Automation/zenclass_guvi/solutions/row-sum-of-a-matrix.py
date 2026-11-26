import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    m = int(data[1])
    
    if n == 0 or m == 0:
        print(-1)
        return
    
    numbers = list(map(int, data[2:2 + n * m]))
    
    row_sums = []
    for i in range(n):
        start_idx = i * m
        end_idx = start_idx + m
        row_sum = sum(numbers[start_idx:end_idx])
        row_sums.append(str(row_sum))
    
    print(' '.join(row_sums))

if __name__ == "__main__":
    main()
