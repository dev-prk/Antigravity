import sys

def print_range(nums, index=0):
    if index >= len(nums):
        return
    print(nums[index], end=' ')
    print_range(nums, index + 1)

def main():
    n = int(sys.stdin.readline().strip())
    if n <= 0:
        print(-1)
        return
    nums = list(range(1, n + 1))
    print_range(nums)

if __name__ == "__main__":
    main()
