import sys
from collections import Counter

def main():
    s = sys.stdin.readline().strip()
    if not s:
        print(-1)
        return
    
    freq = Counter(s)
    unique_chars = [ch for ch, count in freq.items() if count == 1]
    
    if not unique_chars:
        print(-1)
    else:
        print(len(unique_chars))

if __name__ == "__main__":
    main()
