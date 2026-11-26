import sys

def solve():
    data = sys.stdin.read().strip().split()
    if len(data) < 2:
        return
    a, b = map(int, data[:2])
    sys.stdout.write(str(pow(a, b)))

if __name__ == "__main__":
    solve()
