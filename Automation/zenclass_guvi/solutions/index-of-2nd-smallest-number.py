import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    if n <= 0:
        return
    arr = list(map(int, data[1:1+n]))
    
    # Find the smallest value
    min_val = min(arr)
    
    # Find all indices (1-based) where value is min_val
    min_indices = [i for i in range(n) if arr[i] == min_val]
    
    # We need the 2nd smallest. 
    # If there are duplicates of min, the "2nd smallest" is still the smallest value, but at the next index?
    # The problem says "Index of 2nd Smallest Number" and sample output is 1 for input [5,7,4,4,6,8].
    # The smallest number is 4, at indices 3 and 4 (1-based). The 1-based index of the first 4 is 3.
    # But the sample output is 1. That's odd.
    
    # Wait, let's re-read: "Print the smallest number index in an array" in the output description, but the title says "2nd Smallest".
    # Sample: 6\n5 7 4 4 6 8. Output: 1.
    # If we're looking for the 2nd smallest distinct value, that would be 5, at index 1 (1-based). That matches!
    # So it's the 2nd smallest distinct value's first occurrence index (1-based).
    
    # Get unique values sorted
    unique_vals = sorted(set(arr))
    
    if len(unique_vals) < 2:
        # If there's only one unique value, what to do? The problem may not test this, but let's handle.
        # If only one unique value, the 2nd smallest doesn't exist. Output could be -1 or the index of min.
        # Let's assume it's well-formed and there are at least 2 distinct values.
        # But to be safe, if there's only one, output the first index? Or -1?
        # Given constraints, n>0 and numbers can have duplicates. Let's output -1 if less than 2 distinct.
        print(-1)
        return
    
    second_min_val = unique_vals[1]
    
    # Find the first 1-based index of second_min_val
    for i in range(n):
        if arr[i] == second_min_val:
            print(i + 1)
            return
    
    # Should not reach here
    print(-1)

if __name__ == "__main__":
    main()
