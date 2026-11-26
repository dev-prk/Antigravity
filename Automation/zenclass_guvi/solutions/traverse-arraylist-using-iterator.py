import sys
from collections.abc import Iterator

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    
    if n == 0:
        print()
        return
    
    arr = list(map(int, data[1:n+1]))
    
    it = iter(arr)
    
    result = []
    for x in it:
        result.append(str(x))
    
    print(' '.join(result))

if __name__ == "__main__":
    main()
