import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    m = int(data[1])
    multiples = [m * i for i in range(1, n + 1)]
    print(' '.join(map(str, multiples)))

if __name__ == "__main__":
    main()
