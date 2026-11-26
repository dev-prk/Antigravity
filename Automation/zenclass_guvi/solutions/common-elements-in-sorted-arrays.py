import sys

def main() -> None:
    data = list(map(int, sys.stdin.read().split()))
    if not data:
        return
    it = iter(data)
    n = next(it)
    A = [next(it) for _ in range(n)]
    B = [next(it) for _ in range(n)]

    i = j = 0
    res = []
    while i < n and j < n:
        a, b = A[i], B[j]
        if a < b:
            i += 1
        elif a > b:
            j += 1
        else:
            res.append(a)
            # skip duplicates in A
            while i + 1 < n and A[i + 1] == a:
                i += 1
            # skip duplicates in B
            while j + 1 < n and B[j + 1] == b:
                j += 1
            i += 1
            j += 1

    if not res:
        sys.stdout.write("-1")
    else:
        sys.stdout.write(" ".join(map(str, res)))

if __name__ == "__main__":
    main()
