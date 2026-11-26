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
    if len(arr) == 0:
        return
    cnt = Counter(arr)
    min_freq = min(cnt.values())
    elements = [num for num, freq in cnt.items() if freq == min_freq]
    elements.sort(reverse=True)
    print(' '.join(map(str, elements)))

if __name__ == "__main__":
    main()
