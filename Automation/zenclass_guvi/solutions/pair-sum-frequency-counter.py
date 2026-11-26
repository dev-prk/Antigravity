import sys
from collections import defaultdict

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    arr = list(map(int, data[1:1 + n]))
    target = int(data[1 + n])

    freq = defaultdict(int)
    count = 0
    for x in arr:
        complement = target - x
        count += freq[complement]
        freq[x] += 1

    print(count)

if __name__ == "__main__":
    main()
