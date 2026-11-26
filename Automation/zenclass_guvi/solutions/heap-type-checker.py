import sys

def check_heap_type():
    line1 = sys.stdin.readline()
    if not line1:
        print("NONE")
        return
    n = int(line1.strip())
    
    line2 = sys.stdin.readline()
    if not line2:
        print("NONE")
        return
    
    arr = list(map(int, line2.strip().split()))
    
    if n == 0 or len(arr) == 0:
        print("NONE")
        return
    
    is_min_heap = True
    is_max_heap = True
    
    for i in range(n):
        left_idx = 2 * i + 1
        right_idx = 2 * i + 2
        
        if left_idx < n:
            if arr[i] > arr[left_idx]:
                is_min_heap = False
            if arr[i] < arr[left_idx]:
                is_max_heap = False
        
        if right_idx < n:
            if arr[i] > arr[right_idx]:
                is_min_heap = False
            if arr[i] < arr[right_idx]:
                is_max_heap = False
    
    if is_min_heap and not is_max_heap:
        print("MIN")
    elif is_max_heap and not is_min_heap:
        print("MAX")
    else:
        print("NONE")

check_heap_type()
