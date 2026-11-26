import sys

def main():
    line = sys.stdin.readline()
    if not line:
        return
    nums = list(map(int, line.split()))
    if len(nums) == 0:
        print(-1)
    elif len(nums) == 1:
        print(nums[0])
    else:
        nums[0], nums[-1] = nums[-1], nums[0]
        print(' '.join(map(str, nums)))

if __name__ == "__main__":
    main()
