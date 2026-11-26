import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    k = int(data[1])
    arr = list(map(int, data[2:2+n]))
    
    if n == 0 or k == 0:
        print(-1)
        return
    
    if k == 1:
        print(min(arr))
        return
    
    if k == n:
        print(max(arr))
        return
    
    sorted_arr = sorted(arr, reverse=True)
    result = sorted_arr[k-1]
    print(result)

if __name__ == "__main__":
    main()
