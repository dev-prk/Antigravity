import sys
from collections import Counter

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    m = int(data[1])
    
    if n == 0 or m == 0:
        print(-1)
        return
    
    if len(data) < 2 + n + m:
        print(-1)
        return
    
    arr1 = list(map(int, data[2:2+n]))
    arr2 = list(map(int, data[2+n:2+n+m]))
    
    count1 = Counter(arr1)
    count2 = Counter(arr2)
    
    common = []
    for num in count2:
        if num in count1:
            min_count = min(count1[num], count2[num])
            common.extend([num] * min_count)
    
    common.sort()
    
    if not common:
        print(-1)
    else:
        print(' '.join(map(str, common)))

if __name__ == "__main__":
    main()
