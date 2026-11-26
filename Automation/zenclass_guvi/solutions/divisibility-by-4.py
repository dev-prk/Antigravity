import sys

def main():
    s = sys.stdin.read().strip()
    if not s:
        return
    # take last two digits (or the whole number if it's shorter)
    last_two = s[-2:] if len(s) >= 2 else s
    num = int(last_two)
    print("YES" if num % 4 == 0 else "NO")

if __name__ == "__main__":
    main()
