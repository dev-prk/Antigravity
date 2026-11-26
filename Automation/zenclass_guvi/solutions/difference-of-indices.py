import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    
    if n == 0:
        print(0)
        return
    
    arr = list(map(int, data[1:n+1]))
    
    if n == 0 or len(arr) == 0:
        print(0)
        return
    
    max_val = max(arr)
    min_val = min(arr)
    
    max_idx = arr.index(max_val)
    min_idx = arr.index(min_val)
    
    result = max_idx - min_idx
    print(result)

if __name__ == "__main__":
    main()
