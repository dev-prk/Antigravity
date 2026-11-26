import sys

def min_swaps(arr):
    n = len(arr)
    if n <= 1:
        return 0
    
    # Create list of (value, original_index) pairs
    indexed = [(arr[i], i) for i in range(n)]
    
    # Sort by value
    indexed.sort()
    
    # Create position array: pos[i] = current position of element that should be at index i
    pos = [0] * n
    for i in range(n):
        pos[i] = indexed[i][1]
    
    # Find cycles and count swaps
    visited = [False] * n
    swaps = 0
    
    for i in range(n):
        if visited[i] or pos[i] == i:
            continue
        
        cycle_size = 0
        j = i
        while not visited[j]:
            visited[j] = True
            j = pos[j]
            cycle_size += 1
        
        if cycle_size > 1:
            swaps += cycle_size - 1
    
    return swaps

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    
    if n <= 0:
        print(0)
        return
    
    arr = list(map(int, data[1:n+1]))
    print(min_swaps(arr))

if __name__ == "__main__":
    main()
