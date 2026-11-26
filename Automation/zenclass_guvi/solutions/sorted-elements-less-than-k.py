import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    it = iter(data)
    N = int(next(it))
    K = int(next(it))
    arr = [int(next(it)) for _ in range(N)]
    less = [x for x in arr if x < K]
    less.sort()
    if not less:
        print(-1)
    else:
        print(' '.join(map(str, less)))

if __name__ == "__main__":
    main()
