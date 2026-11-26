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
    
    max_val = arr[0]
    max_idx = 0
    
    for i in range(1, n):
        if arr[i] > max_val:
            max_val = arr[i]
            max_idx = i
    
    print(max_idx)

if __name__ == "__main__":
    main()
