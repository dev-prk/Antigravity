import sys
from collections import Counter

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        return
    numbers = list(map(int, data[1:n+1]))
    if not numbers:
        return
    counts = Counter(numbers)
    max_count = max(counts.values())
    max_repeating = min(num for num, cnt in counts.items() if cnt == max_count)
    print(max_repeating)

if __name__ == "__main__":
    main()
