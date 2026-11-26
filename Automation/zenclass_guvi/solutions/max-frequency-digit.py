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
    if not arr:
        return
    freq = Counter(arr)
    max_freq = max(freq.values())
    for num in arr:
        if freq[num] == max_freq:
            print(num)
            return

if __name__ == "__main__":
    main()
