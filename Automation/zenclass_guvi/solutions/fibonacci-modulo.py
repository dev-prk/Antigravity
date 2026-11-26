import sys

def fibonacci_mod(n, m):
    if n == 0:
        return 0
    if m == 1:
        return 0
    
    prev, curr = 0, 1
    for i in range(1, n):
        prev, curr = curr, (prev + curr) % m
    
    return curr

def main():
    line = sys.stdin.readline().strip()
    if not line:
        return
    parts = line.split(',')
    n = int(parts[0].split('=')[1])
    m = int(parts[1].split('=')[1])
    result = fibonacci_mod(n, m)
    print(result)

if __name__ == "__main__":
    main()
