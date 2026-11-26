import sys
from collections import Counter

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        return
    nums = list(map(int, data[1:1+n]))
    cnt = Counter(nums)
    min_freq = min(cnt.values())
    least = [x for x, v in cnt.items() if v == min_freq]
    least.sort(reverse=True)
    print(' '.join(map(str, least)))

if __name__ == "__main__":
    main()
