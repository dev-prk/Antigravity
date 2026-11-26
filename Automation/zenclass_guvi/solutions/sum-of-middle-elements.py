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
    
    if len(data) < 2 * n + 1:
        print(-1)
        return
    
    arr1 = list(map(int, data[1:n+1]))
    arr2 = list(map(int, data[n+1:2*n+1]))
    
    merged = arr1 + arr2
    merged.sort()
    
    mid = len(merged) // 2
    result = merged[mid - 1] + merged[mid]
    
    print(result)

if __name__ == "__main__":
    main()
