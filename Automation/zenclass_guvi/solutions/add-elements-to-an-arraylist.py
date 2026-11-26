import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    elements = list(map(int, data[1:n+1]))
    print(' '.join(map(str, elements)))

if __name__ == "__main__":
    main()
