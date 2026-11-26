import sys

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    it = iter(data)
    try:
        m1 = int(next(it))
        n1 = int(next(it))
    except StopIteration:
        return

    mat1 = [int(next(it)) for _ in range(m1 * n1)]

    try:
        m2 = int(next(it))
        n2 = int(next(it))
    except StopIteration:
        # incomplete second matrix -> not equal
        print("Not equal")
        return

    mat2 = [int(next(it)) for _ in range(m2 * n2)]

    if m1 == m2 and n1 == n2 and mat1 == mat2:
        print("Equal")
    else:
        print("Not equal")

if __name__ == "__main__":
    solve()
