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
    
    arr = list(map(int, data[1:n+1]))
    
    if not arr:
        print(-1)
        return
    
    min_val = arr[0]
    max_val = arr[0]
    min_idx = 0
    max_idx = 0
    
    for i in range(1, len(arr)):
        if arr[i] < min_val:
            min_val = arr[i]
            min_idx = i
        if arr[i] > max_val:
            max_val = arr[i]
            max_idx = i
    
    result = abs(min_idx - max_idx)
    print(result)

if __name__ == "__main__":
    main()
