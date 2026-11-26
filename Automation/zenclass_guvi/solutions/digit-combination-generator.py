import sys
from itertools import permutations

def main():
    line = sys.stdin.readline().strip()
    if not line:
        return
    nums = [int(x) for x in line.split()]
    nums_str = [str(x) for x in nums]
    for perm in permutations(nums_str):
        print(' '.join(perm))

if __name__ == "__main__":
    main()
