import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    m = int(data[1])
    keys = list(map(int, data[2:2+n]))
    
    table = [-1] * n
    
    for key in keys:
        idx = key % n
        if table[idx] == -1:
            table[idx] = key
        else:
            i = 1
            while i < n:
                new_idx = (idx + i * i) % n
                if table[new_idx] == -1:
                    table[new_idx] = key
                    break
                i += 1
    
    print(' '.join(map(str, table)))

if __name__ == "__main__":
    main()
