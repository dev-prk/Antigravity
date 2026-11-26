import sys

def solve():
    data = sys.stdin.read().strip()
    if not data:
        return
    n = int(data)
    for i in range(1, n + 1):
        print('*' * i)
    for i in range(n - 1, 0, -1):
        print('*' * i)

if __name__ == "__main__":
    solve()
