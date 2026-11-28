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
    
    # Standard bubble sort
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    
    print(' '.join(map(str, arr)) + ' ')

if __name__ == "__main__":
    main()
