import sys

def counting_sort(arr):
    if not arr:
        return arr
    
    min_val = min(arr)
    max_val = max(arr)
    
    # Handle case where all elements are the same
    if min_val == max_val:
        return arr
    
    range_size = max_val - min_val + 1
    count = [0] * range_size
    
    # Store count of each element
    for num in arr:
        count[num - min_val] += 1
    
    # Update count array to store cumulative count
    for i in range(1, len(count)):
        count[i] += count[i - 1]
    
    # Create result array
    result = [0] * len(arr)
    
    # Build the result array
    for num in arr:
        idx = num - min_val
        result[count[idx] - 1] = num
        count[idx] -= 1
    
    return result

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    if n == 0:
        print("")
        return
    
    arr = list(map(int, data[1:n+1]))
    sorted_arr = counting_sort(arr)
    print(' '.join(map(str, sorted_arr)))

if __name__ == "__main__":
    main()
