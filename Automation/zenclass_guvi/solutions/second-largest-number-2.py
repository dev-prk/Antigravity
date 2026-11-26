import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    nums = list(map(int, data))
    if len(nums) < 2:
        print(-1)
        return
    unique_nums = set(nums)
    if len(unique_nums) < 2:
        print(-1)
        return
    sorted_nums = sorted(unique_nums)
    print(sorted_nums[-2])

if __name__ == "__main__":
    main()
