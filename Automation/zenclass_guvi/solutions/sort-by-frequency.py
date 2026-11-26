import sys
from collections import Counter

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    arr = list(map(int, data[1:1+n]))
    freq = Counter(arr)
    first_index = {}
    for i, val in enumerate(arr):
        if val not in first_index:
            first_index[val] = i
    sorted_arr = sorted(arr, key=lambda x: (-freq[x], first_index[x]))
    print(' '.join(map(str, sorted_arr)))

if __name__ == "__main__":
    main()
