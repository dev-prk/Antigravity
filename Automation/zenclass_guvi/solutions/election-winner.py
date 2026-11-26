import sys
from collections import Counter

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    cnt = Counter(data)
    max_votes = max(cnt.values())
    winner = min(name for name, v in cnt.items() if v == max_votes)
    print(winner, max_votes)

if __name__ == "__main__":
    main()
