import sys
from collections import Counter

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print('no')
        return
    
    n = int(data[0])
    m = int(data[1])
    
    if m == 0:
        print('yes')
        return
    
    if n == 0:
        print('no')
        return
    
    arr_a = list(map(int, data[2:2+n]))
    arr_b = list(map(int, data[2+n:2+n+m]))
    
    count_a = Counter(arr_a)
    count_b = Counter(arr_b)
    
    for num, cnt in count_b.items():
        if count_a[num] < cnt:
            print('no')
            return
    
    print('yes')

if __name__ == "__main__":
    main()
