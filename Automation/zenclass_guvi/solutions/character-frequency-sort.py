import sys
from collections import Counter

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        return
    arr = list(map(int, data[1:n+1]))
    freq = Counter(arr)
    items = list(freq.items())
    items.sort(key=lambda x: (-x[1], -x[0]))
    result = [str(item[0]) for item in items]
    print(' '.join(result))

if __name__ == "__main__":
    main()
