import sys

def solve():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    nums = list(map(int, data[1:1 + n]))
    if n == 0:
        return
    mid_index = (n - 1) // 2
    del nums[mid_index]
    print(' '.join(map(str, nums)))

if __name__ == "__main__":
    solve()
