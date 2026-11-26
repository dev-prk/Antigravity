import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    
    if n == 0:
        print()
        return
    
    arr = list(map(int, data[1:n+1]))
    
    indexed = [(arr[i], i) for i in range(n)]
    
    indexed.sort(key=lambda x: x[0])
    
    result = [str(indexed[i][1] + 1) for i in range(n)]
    
    print(' '.join(result))

if __name__ == "__main__":
    main()
