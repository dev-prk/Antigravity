import sys

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    nums = list(map(int, data[1:1 + n]))
    total = sum(x for x in nums if x < 0)
    sys.stdout.write(str(total))

if __name__ == "__main__":
    solve()
