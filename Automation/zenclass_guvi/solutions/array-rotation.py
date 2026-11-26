import sys

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    it = iter(data)
    try:
        n = int(next(it))
        d = int(next(it))
    except StopIteration:
        return
    arr = []
    for _ in range(n):
        try:
            arr.append(int(next(it)))
        except StopIteration:
            break
    if n == 0:
        sys.stdout.write("")
        return
    d %= n
    rotated = arr[d:] + arr[:d]
    sys.stdout.write(" ".join(map(str, rotated)))

if __name__ == "__main__":
    solve()
