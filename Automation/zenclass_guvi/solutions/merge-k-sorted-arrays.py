import sys
import heapq

def merge_k_sorted_arrays():
    lines = sys.stdin.read().strip().split('\n')
    if not lines:
        return
    
    k = int(lines[0].strip())
    arrays = []
    index = 1
    
    for i in range(k):
        if index < len(lines):
            line = lines[index].strip()
            if line:
                arr = list(map(int, line.split()))
                arrays.append(arr)
            else:
                arrays.append([])
            index += 1
    
    if k == 0:
        print("")
        return
    
    min_heap = []
    for i, arr in enumerate(arrays):
        if arr:
            heapq.heappush(min_heap, (arr[0], i, 0))
    
    result = []
    while min_heap:
        val, arr_idx, elem_idx = heapq.heappop(min_heap)
        result.append(val)
        if elem_idx + 1 < len(arrays[arr_idx]):
            heapq.heappush(min_heap, (arrays[arr_idx][elem_idx + 1], arr_idx, elem_idx + 1))
    
    print(' '.join(map(str, result)))

if __name__ == "__main__":
    merge_k_sorted_arrays()
