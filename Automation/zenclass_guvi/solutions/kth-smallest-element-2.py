import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    idx = 0
    t = int(data[idx])
    idx += 1
    
    results = []
    
    for _ in range(t):
        n = int(data[idx])
        idx += 1
        
        arr = []
        for _ in range(n):
            arr.append(int(data[idx]))
            idx += 1
        
        k = int(data[idx])
        idx += 1
        
        arr.sort()
        results.append(str(arr[k - 1]))
    
    print('\n'.join(results))

if __name__ == "__main__":
    main()
