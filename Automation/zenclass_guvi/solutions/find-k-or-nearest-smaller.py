import sys

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    it = iter(data)
    try:
        n = int(next(it))
        k = int(next(it))
    except StopIteration:
        return

    max_less = None
    found = False
    for _ in range(n):
        try:
            val = int(next(it))
        except StopIteration:
            break
        if val == k:
            found = True
        elif val < k:
            if max_less is None or val > max_less:
                max_less = val

    if found:
        print(k)
    elif max_less is not None:
        print(max_less)
    else:
        print(-1)

if __name__ == "__main__":
    solve()
