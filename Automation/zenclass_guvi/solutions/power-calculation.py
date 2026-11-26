import sys

def solve():
    data = sys.stdin.read().strip().split()
    if len(data) < 2:
        return
    try:
        n = int(data[0])
        m = int(data[1])
    except:
        return
    print(pow(n, m))

if __name__ == "__main__":
    solve()
