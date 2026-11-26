import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    n = int(data)
    if n == 0:
        print(0)
        return
    # Find the position of the first 1 from the right (1-indexed)
    pos = 0
    m = n
    while m:
        pos += 1
        if m & 1:
            print(pos)
            return
        m >>= 1
    print(0)

if __name__ == "__main__":
    main()
