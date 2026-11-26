import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    m = int(data[1])
    
    if n == 0:
        print(-1)
        return
    
    arr = list(map(int, data[2:2+n]))
    
    result = [x for x in arr if x != m]
    
    if len(result) == len(arr):
        print(-1)
    else:
        print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
