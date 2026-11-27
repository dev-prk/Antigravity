import sys
from collections import Counter

def main():
    data = sys.stdin.read().splitlines()
    if not data:
        print(-1)
        return
    n = int(data[0].strip())
    if n == 0:
        print(-1)
        return
    original = [line.strip() for line in data[1:1+n]]
    shifted = [s[::-1] for s in original]
    original_count = Counter(original)
    shifted_count = Counter(shifted)
    result = 0
    for word in original_count:
        if word in shifted_count:
            result += original_count[word]
    print(result)

if __name__ == "__main__":
    main()
