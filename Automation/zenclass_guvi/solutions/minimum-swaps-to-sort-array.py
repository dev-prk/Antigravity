import sys

def min_swaps_to_sort(arr):
    n = len(arr)
    if n <= 1:
        return 0
    
    # Create list of (value, original_index) pairs
    indexed_arr = [(arr[i], i) for i in range(n)]
    
    # Sort by value
    indexed_arr.sort(key=lambda x: x[0])
    
    # Track visited nodes
    visited = [False] * n
    
    swaps = 0
    
    for i in range(n):
        # If already visited or element is at correct position
        if visited[i] or indexed_arr[i][1] == i:
            continue
        
        # Find cycle size
        cycle_size = 0
        j = i
        while not visited[j]:
            visited[j] = True
            j = indexed_arr[j][1]
            cycle_size += 1
        
        # Add swaps for this cycle
        if cycle_size > 0:
            swaps += (cycle_size - 1)
    
    return swaps

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    if n == 0:
        print(0)
        return
    
    arr = list(map(int, data[1:n+1]))
    result = min_swaps_to_sort(arr)
    print(result)

if __name__ == "__main__":
    main()
