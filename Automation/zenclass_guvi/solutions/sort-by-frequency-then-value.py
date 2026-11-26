import sys
from collections import Counter

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        print("")
        return
    arr = list(map(int, data[1:n+1]))
    freq = Counter(arr)
    unique_vals = list(freq.keys())
    sorted_vals = sorted(unique_vals, key=lambda x: (freq[x], x))
    result = [str(x) for x in sorted_vals]
    print(" ".join(result))

if __name__ == "__main__":
    main()
