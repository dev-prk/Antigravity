import sys
from collections import Counter

def main():
    s = sys.stdin.readline().rstrip('\n')
    cnt = Counter(s)
    seen = set()
    out = []
    for ch in s:
        if cnt[ch] > 1 and ch not in seen:
            out.append(ch)
            seen.add(ch)
    if not out:
        print(-1)
    else:
        print(' '.join(out))

if __name__ == "__main__":
    main()
