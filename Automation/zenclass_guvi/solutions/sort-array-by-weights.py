import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    
    if n == 0:
        print("")
        return
    
    arr = list(map(int, data[1:1+n]))
    weights = list(map(int, data[1+n:1+2*n]))
    
    pairs = list(zip(weights, arr))
    pairs.sort(key=lambda x: x[0])
    
    result = [str(p[1]) for p in pairs]
    print(" ".join(result))

if __name__ == "__main__":
    main()
