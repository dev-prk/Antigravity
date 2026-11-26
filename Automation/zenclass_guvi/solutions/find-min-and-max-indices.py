import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    nums = list(map(int, data[1:1 + n]))
    if n == 0:
        return
    min_val = nums[0]
    max_val = nums[0]
    min_idx = 0
    max_idx = 0
    for i in range(1, n):
        if nums[i] < min_val:
            min_val = nums[i]
            min_idx = i
        if nums[i] > max_val:
            max_val = nums[i]
            max_idx = i
    # The problem asks for min and max indices (1-based) in order "min_idx max_idx"
    # But looking at sample 3: Input 5 3 4 1 3, min is 1 at index 4, max is 5 at index 1. Output is "4 1".
    # So it's "min_index max_index"
    print(f"{min_idx + 1} {max_idx + 1}")

if __name__ == "__main__":
    main()
