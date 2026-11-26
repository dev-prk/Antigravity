import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    k = int(data[1])
    
    if n == 0:
        print()
        return
    
    arr = list(map(int, data[2:2+n]))
    
    effective_k = k % n
    
    if effective_k == 0:
        result = arr
    else:
        result = arr[-effective_k:] + arr[:-effective_k]
    
    print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
