import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    it = iter(data)
    N = int(next(it))
    K = int(next(it))
    arr = [int(next(it)) for _ in range(N)]
    res = arr[:N - K]
    if res:
        sys.stdout.write(' '.join(map(str, res)))

if __name__ == "__main__":
    main()
