import sys
from collections import Counter

def main():
    data = sys.stdin.buffer.read().split()
    if not data:
        return

    n = int(data[0])
    nums = list(map(int, data[1:1 + n]))

    counts = Counter(nums)
    result = [str(x) for x in nums if counts[x] == 1]

    sys.stdout.write(" ".join(result) + "\n")

if __name__ == "__main__":
    main()
