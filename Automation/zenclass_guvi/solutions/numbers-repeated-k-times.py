import sys
from collections import Counter

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
    
    freq = Counter(arr)
    
    result = [num for num, count in freq.items() if count == k]
    result.sort()
    
    if not result:
        print(-1)
    else:
        print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
