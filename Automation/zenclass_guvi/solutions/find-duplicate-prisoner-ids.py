import sys
from collections import Counter

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    
    if n == 0:
        print(-1)
        return
    
    if len(data) < 2:
        print(-1)
        return
    
    ids = list(map(int, data[1:1+n]))
    
    if len(ids) == 0:
        print(-1)
        return
    
    count = Counter(ids)
    duplicates = [x for x in ids if count[x] > 1]
    
    if not duplicates:
        print(-1)
    else:
        seen = set()
        result = []
        for x in duplicates:
            if x not in seen:
                result.append(str(x))
                seen.add(x)
        print(' '.join(result))

if __name__ == "__main__":
    main()
