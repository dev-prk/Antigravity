import sys

def solve():
    t = int(sys.stdin.readline().strip())
    for _ in range(t):
        n = int(sys.stdin.readline().strip())
        print(n // 2)

if __name__ == "__main__":
    solve()
