import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    
    if n == 0 or n < 2:
        print(-1)
        return
    
    if len(data) < n + 1:
        print(-1)
        return
    
    arr = list(map(int, data[1:n+1]))
    
    if len(arr) < 2:
        print(-1)
        return
    
    first = second = float('-inf')
    
    for num in arr:
        if num > first:
            second = first
            first = num
        elif num > second and num != first:
            second = num
    
    if second == float('-inf'):
        print(-1)
    else:
        print(second)

if __name__ == "__main__":
    main()
