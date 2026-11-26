import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    k = int(data[1])
    
    if n == 0:
        print(-1)
        return
    
    arr = list(map(int, data[2:2+n]))
    
    for i in range(n):
        if arr[i] == k:
            print(i + 1)
            return
    
    print(-1)

if __name__ == "__main__":
    main()
