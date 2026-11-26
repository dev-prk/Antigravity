import sys

def main():
    s = sys.stdin.readline().strip()
    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    for ch, cnt in freq.items():
        print(f"{ch} {cnt}")

if __name__ == "__main__":
    main()
