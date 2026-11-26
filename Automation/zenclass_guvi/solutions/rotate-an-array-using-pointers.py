import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    arr = list(map(int, data[1:n+1]))
    k = int(data[n+1])
    
    if n == 0:
        print()
        return
    
    k = k % n
    
    if k == 0:
        print(' '.join(map(str, arr)))
        return
    
    def reverse(start, end):
        while start < end:
            arr[start], arr[end] = arr[end], arr[start]
            start += 1
            end -= 1
    
    reverse(0, n - 1)
    reverse(0, k - 1)
    reverse(k, n - 1)
    
    print(' '.join(map(str, arr)))

if __name__ == "__main__":
    main()
