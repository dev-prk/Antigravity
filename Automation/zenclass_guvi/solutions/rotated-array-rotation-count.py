import sys

def find_rotation_count(arr):
    n = len(arr)
    if n == 0:
        return -1
    
    # Check if array is not rotated (already sorted)
    is_sorted = True
    for i in range(n - 1):
        if arr[i] > arr[i + 1]:
            is_sorted = False
            break
    
    if is_sorted:
        return -1
    
    # Binary search to find the minimum element (pivot point)
    left, right = 0, n - 1
    
    while left < right:
        mid = (left + right) // 2
        
        if arr[mid] > arr[right]:
            # Minimum is in the right half
            left = mid + 1
        elif arr[mid] < arr[right]:
            # Minimum is in the left half (including mid)
            right = mid
        else:
            # arr[mid] == arr[right], can't determine which half
            # decrement right to skip duplicate
            right -= 1
    
    # Find position of minimum element
    # Count how many positions it was shifted
    min_idx = -1
    for i in range(n):
        if arr[i] == arr[left]:
            min_idx = i
            break
    
    if min_idx == -1:
        return -1
    
    # The rotation count is the index of minimum element
    # But we need to verify if rotation actually happened
    if min_idx == 0:
        # Check if actually sorted
        is_actual_sorted = True
        for i in range(n - 1):
            if arr[i] > arr[i + 1]:
                is_actual_sorted = False
                break
        if is_actual_sorted:
            return -1
    
    return min_idx

def main():
    # Read all input
    data = sys.stdin.read().strip().split()
    
    if not data:
        return
    
    M = int(data[0])
    arr = list(map(int, data[1:M+1]))
    
    result = find_rotation_count(arr)
    print(result)

if __name__ == "__main__":
    main()
