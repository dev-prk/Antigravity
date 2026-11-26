import sys
from collections import Counter

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    m = int(data[1])
    
    a1 = list(map(int, data[2:2+n]))
    a2 = list(map(int, data[2+n:2+n+m]))
    
    count_a1 = Counter(a1)
    
    result = []
    
    for val in a2:
        if val in count_a1:
            result.extend([val] * count_a1[val])
            del count_a1[val]
    
    remaining = []
    for val, cnt in count_a1.items():
        remaining.extend([val] * cnt)
    
    remaining.sort()
    result.extend(remaining)
    
    print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
