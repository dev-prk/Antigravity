import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    numbers = list(map(int, data[1:n+1]))
    numbers.sort()
    print(' '.join(map(str, numbers)))

if __name__ == "__main__":
    main()
