import sys
from collections import Counter

def main():
    lines = sys.stdin.read().splitlines()
    s1 = lines[0] if len(lines) > 0 else ''
    s2 = lines[1] if len(lines) > 1 else ''
    print('1' if Counter(s1) == Counter(s2) else '-1')

if __name__ == "__main__":
    main()
