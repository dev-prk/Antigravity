import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    m = int(data[0])
    n = int(data[1]) if len(data) > 1 else 0
    keys = list(map(int, data[2:2 + n]))
    table = [-1] * m
    for key in keys:
        table[key % m] = key
    print(' '.join(map(str, table)))

if __name__ == '__main__':
    main()
