import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    if n <= 0:
        print(0)
        return
    nums = list(map(int, data[1:1 + n]))
    if not nums:
        print(0)
        return
    print(min(nums) + max(nums))

if __name__ == "__main__":
    main()
