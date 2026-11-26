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
    
    if n == 1:
        print(-1)
        return
    
    max_len = 1
    current_len = 1
    
    for i in range(1, n):
        if arr[i] > arr[i-1]:
            current_len += 1
            max_len = max(max_len, current_len)
        else:
            current_len = 1
    
    if max_len == 1:
        print(-1)
    else:
        print(max_len)

if __name__ == "__main__":
    main()
