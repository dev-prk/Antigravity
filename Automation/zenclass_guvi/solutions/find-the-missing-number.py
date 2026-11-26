import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    if len(data) < 2:
        print(1)
        return
    
    nums = list(map(int, data[1:]))
    
    # Handle case where we don't have exactly n-1 numbers
    if len(nums) == 0:
        print(1)
        return
    
    # Method: Calculate expected sum vs actual sum
    expected_sum = n * (n + 1) // 2
    actual_sum = sum(nums)
    missing = expected_sum - actual_sum
    
    # Edge case: if all numbers present, missing should be the one not in the range
    if missing == 0 or missing > n or missing < 0:
        # Find the number that's actually missing
        present = set(nums)
        for i in range(1, n + 1):
            if i not in present:
                missing = i
                break
    
    print(missing)

if __name__ == "__main__":
    main()
