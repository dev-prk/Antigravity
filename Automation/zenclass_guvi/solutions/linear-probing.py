import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    m = int(data[0])
    n = int(data[1])
    
    if n == 0:
        print(' '.join(['-1'] * m))
        return
    
    keys = list(map(int, data[2:2+n]))
    
    table = [-1] * m
    
    for key in keys:
        idx = key % m
        while table[idx] != -1:
            idx = (idx + 1) % m
        table[idx] = key
    
    print(' '.join(map(str, table)))

if __name__ == "__main__":
    main()
