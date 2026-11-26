import sys
from collections import Counter

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    arr = list(map(int, data[1:1+n]))
    cnt = Counter(arr)
    for x in arr:
        if cnt[x] == 1:
            print(x)
            return
    print(0)

if __name__ == "__main__":
    main()
