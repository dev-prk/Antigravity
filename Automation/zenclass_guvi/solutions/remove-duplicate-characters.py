import sys
from collections import Counter

def main() -> None:
    s = sys.stdin.readline().rstrip('\n')
    cnt = Counter(s)
    # Build result preserving order, keeping only chars with count == 1
    result = ''.join(ch for ch in s if cnt[ch] == 1)
    sys.stdout.write(result)

if __name__ == "__main__":
    main()
