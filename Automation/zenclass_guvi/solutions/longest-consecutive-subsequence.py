import sys

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    nums = list(map(int, data[1:1 + n])) if n > 0 else []
    if not nums:
        print(0)
        return

    num_set = set(nums)
    longest = 0

    for x in num_set:
        if x - 1 not in num_set:          # start of a sequence
            current = x
            length = 1
            while current + 1 in num_set:
                current += 1
                length += 1
            if length > longest:
                longest = length

    print(longest)

if __name__ == "__main__":
    solve()
