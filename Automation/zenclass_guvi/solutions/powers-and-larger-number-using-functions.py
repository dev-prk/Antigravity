import sys

def power(base, exponent=None):
    if exponent is None:
        return base ** 2
    return base ** exponent

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    a = int(data[0])
    b = int(data[1]) if len(data) > 1 else 0
    # According to problem, both are given.
    print(power(a))
    print(power(a, b))
    print(power(b, a))
    print(max(a, b))

if __name__ == "__main__":
    solve()
