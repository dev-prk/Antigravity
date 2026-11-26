import sys
from collections import Counter

def main():
    data = sys.stdin.read().split()
    if len(data) < 2:
        s1 = data[0] if data else ''
        s2 = input().strip()
    else:
        s1, s2 = data[0], data[1]

    if s1 != s1[::-1] or s2 != s2[::-1]:
        print(0)
        return

    print(1 if Counter(s1) == Counter(s2) else 0)

if __name__ == "__main__":
    main()
