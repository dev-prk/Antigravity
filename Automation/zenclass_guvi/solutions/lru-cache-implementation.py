import sys
from collections import OrderedDict

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    k = int(data[1])
    
    if n == 0 or k == 0:
        print(-1)
        return
    
    queries = list(map(int, data[2:2+n]))
    
    cache = OrderedDict()
    
    for val in queries:
        if val in cache:
            cache.move_to_end(val)
        else:
            cache[val] = True
            if len(cache) > k:
                cache.popitem(last=False)
    
    if not cache:
        print(-1)
    else:
        print(' '.join(map(str, cache.keys())))

if __name__ == "__main__":
    main()
