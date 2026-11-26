import sys
from collections import Counter

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
    count = Counter(arr)
    
    result = 0
    for val in count.values():
        result += val // 3
    
    print(result)

if __name__ == "__main__":
    main()
