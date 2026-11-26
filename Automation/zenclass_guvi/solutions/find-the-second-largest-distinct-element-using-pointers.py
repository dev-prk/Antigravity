import sys

def secondLargest(arr, n):
    if n < 2:
        return -1
    
    max_val = arr[0]
    second_max = None
    
    # Use pointer-based traversal
    i = 0
    while i < n:
        current = arr[i]
        
        if current > max_val:
            second_max = max_val
            max_val = current
        elif current != max_val:
            if second_max is None or current > second_max:
                second_max = current
        
        i += 1
    
    return second_max if second_max is not None else -1

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    
    if n == 0:
        print(-1)
        return
    
    if len(data) < n + 1:
        print(-1)
        return
    
    arr = list(map(int, data[1:n+1]))
    result = secondLargest(arr, n)
    print(result)

if __name__ == "__main__":
    main()
