import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    
    n = int(data[0])
    if n <= 1:
        return
    
    arr = list(map(int, data[1:n+1]))
    result = []
    
    for i in range(1, len(arr)):
        if arr[i] % arr[i-1] == 0:
            result.append(str(arr[i]))
    
    if result:
        print(' '.join(result))

if __name__ == "__main__":
    main()
