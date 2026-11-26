import sys

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    nums = list(map(int, data[1:1 + n])) if n > 0 else []
    print(sum(nums))

if __name__ == "__main__":
    solve()
