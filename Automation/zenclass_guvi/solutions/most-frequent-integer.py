import sys
from collections import Counter

def main():
    line = sys.stdin.readline().strip()
    if not line:
        return
    nums = list(map(int, line.split()))
    if not nums:
        return
    counts = Counter(nums)
    max_count = max(counts.values())
    candidates = [num for num, cnt in counts.items() if cnt == max_count]
    result = min(candidates)
    print(result)

if __name__ == "__main__":
    main()
