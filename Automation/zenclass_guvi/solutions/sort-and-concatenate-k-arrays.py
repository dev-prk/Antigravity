import sys

def main():
    k = int(sys.stdin.readline().strip())
    result = []
    for _ in range(k):
        n = int(sys.stdin.readline().strip())
        elements = list(map(int, sys.stdin.readline().split()))
        elements.sort()
        result.extend(elements)
    print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
