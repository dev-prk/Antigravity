import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    s = data[0].strip()
    total = 0
    for ch in s:
        if ch.isdigit():
            d = int(ch)
            total += d * d
    print(total)

if __name__ == "__main__":
    main()
