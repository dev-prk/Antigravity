import sys
from collections import Counter

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    nums = list(map(int, data[1:1+n]))
    cnt = Counter(nums)
    seen = set()
    res = []
    for x in nums:
        if cnt[x] > 1 and x not in seen:
            res.append(str(x))
            seen.add(x)
    if res:
        sys.stdout.write(' '.join(res))

if __name__ == "__main__":
    main()
