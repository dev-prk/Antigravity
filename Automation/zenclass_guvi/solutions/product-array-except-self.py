import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    
    if n == 0:
        print(-1)
        return
    
    arr = list(map(int, data[1:n+1]))
    
    if n == 1:
        print(-1)
        return
    
    result = [1] * n
    
    # Left products
    for i in range(1, n):
        result[i] = result[i-1] * arr[i-1]
    
    # Right products and combine
    right_product = 1
    for i in range(n-1, -1, -1):
        result[i] *= right_product
        right_product *= arr[i]
    
    # Check if any result is zero
    if 0 in result:
        print(-1)
        return
    
    print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
