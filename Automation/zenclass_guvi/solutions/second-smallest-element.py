import sys

def solve() -> None:
    data = list(map(int, sys.stdin.read().split()))
    if not data:
        return
    n = data[0]
    arr = data[1:1 + n] if len(data) >= 1 + n else data[1:]

    if n < 2:
        sys.stdout.write("-1")
        return

    min1 = None   # smallest
    min2 = None   # second smallest (distinct)

    for x in arr:
        if min1 is None or x < min1:
            if min1 is not None and x != min1:
                # previous smallest becomes candidate for second smallest
                if min2 is None or min1 < min2:
                    min2 = min1
            min1 = x
        elif x != min1:
            if min2 is None or x < min2:
                min2 = x

    sys.stdout.write(str(min2) if min2 is not None else "-1")

if __name__ == "__main__":
    solve()
