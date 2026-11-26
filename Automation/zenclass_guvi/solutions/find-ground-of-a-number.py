import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    k = int(data[1])
    
    if n == 0 or len(data) < 2 + n:
        print(-1)
        return
    
    arr = list(map(int, data[2:2+n]))
    
    result_index = -1
    
    for i in range(n):
        if arr[i] <= k:
            result_index = i
        else:
            break
    
    print(result_index)

if __name__ == "__main__":
    main()
