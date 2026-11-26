import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    nums = list(map(int, data[1:1 + n]))
    if n == 0:
        return
    # middle index for even case -> second middle
    # For odd: n=5, middle index=2 (0-based)
    # For even: n=4, second middle index=2 (0-based), i.e., n//2
    idx = n // 2
    print(nums[idx])

if __name__ == '__main__':
    main()
