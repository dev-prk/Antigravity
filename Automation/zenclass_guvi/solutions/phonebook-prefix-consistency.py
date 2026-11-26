import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    nums = data[1:1+n]
    # Sort and check if any number is a prefix of its successor
    nums.sort()
    for i in range(n - 1):
        if nums[i+1].startswith(nums[i]):
            print("Inconsistent")
            return
    print("Consistent")

if __name__ == "__main__":
    main()
