import sys
from collections import Counter

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        return
    ids = [int(x) for x in data[1:1 + n]]
    if not ids:
        return
    counts = Counter(ids)
    max_count = max(counts.values())
    # Find all with max count, pick smallest id
    best = min(cid for cid, cnt in counts.items() if cnt == max_count)
    print(f"{best} {max_count}")

if __name__ == "__main__":
    main()
