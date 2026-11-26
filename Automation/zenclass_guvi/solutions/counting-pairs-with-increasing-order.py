import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    if n <= 1:
        print(0)
        return
    
    arr = list(map(int, data[1:n+1]))
    if len(arr) < n:
        print(0)
        return
    
    # Sort and use merge sort approach for counting inversions
    # Actually, we need to count pairs (i, j) where i < j and arr[i] < arr[j]
    # This is total pairs minus inversions
    # Total pairs = n*(n-1)/2
    # Count inversions using merge sort
    
    def merge_sort_count(arr):
        if len(arr) <= 1:
            return arr, 0
        mid = len(arr) // 2
        left, inv_left = merge_sort_count(arr[:mid])
        right, inv_right = merge_sort_count(arr[mid:])
        merged = []
        inv = inv_left + inv_right
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                inv += len(left) - i
                j += 1
        merged.extend(left[i:])
        merged.extend(right[j:])
        return merged, inv
    
    _, inversions = merge_sort_count(arr)
    total_pairs = n * (n - 1) // 2
    answer = total_pairs - inversions
    print(answer)

if __name__ == "__main__":
    main()
