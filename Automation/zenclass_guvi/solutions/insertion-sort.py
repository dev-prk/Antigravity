import sys

def main():
    data = sys.stdin.read().splitlines()
    if not data:
        return
    n = int(data[0].strip())
    if n == 0:
        print()
        return
    if len(data) < 2:
        nums = []
    else:
        nums = list(map(int, data[1].split()))
    if len(nums) > n:
        nums = nums[:n]
    elif len(nums) < n:
        nums.extend([0] * (n - len(nums)))
    for i in range(1, n):
        key = nums[i]
        j = i - 1
        while j >= 0 and nums[j] > key:
            nums[j + 1] = nums[j]
            j -= 1
        nums[j + 1] = key
    print(' '.join(map(str, nums)), end=' ')

if __name__ == "__main__":
    main()
