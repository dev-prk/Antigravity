import sys

def solve() -> None:
    data = sys.stdin.read().strip()
    if not data:
        return
    n = int(data)

    if n == 0:
        print("ZeRo")
    elif n > 0:
        fib = []
        a, b = 1, 1
        for _ in range(n):
            fib.append(str(a))
            a, b = b, a + b
        print(" ".join(fib))

if __name__ == "__main__":
    solve()
