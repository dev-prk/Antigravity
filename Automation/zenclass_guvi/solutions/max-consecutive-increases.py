import sys

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    nums = list(map(int, data[1:1 + max(0, n)]))
    if n <= 0 or not nums:
        print(0)
        return
    max_len = cur = 1
    for i in range(1, len(nums)):
        if nums[i] > nums[i - 1]:
            cur += 1
        else:
            cur = 1
        if cur > max_len:
            max_len = cur
    print(max_len)

if __name__ == "__main__":
    solve()
