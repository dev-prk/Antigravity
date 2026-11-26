import sys

def main():
    data = sys.stdin.read().split()
    if len(data) < 3:
        return
    n = int(data[0])
    L = int(data[1])
    R = int(data[2])
    mask = ((1 << (R - L + 1)) - 1) << (L - 1)
    print(n | mask)

if __name__ == "__main__":
    main()
