import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    if n <= 0:
        return
    arr = []
    idx = 1
    for i in range(n):
        arr.append(int(data[idx]))
        idx += 1
    
    # Find the second largest index (1-based)
    # We need to find the index of the second largest element
    # If there are duplicates, we consider distinct values? 
    # Let's re-read problem statement: "Print the index 2nd largest number in an array"
    # Sample: 5 7 4 4 6 8 -> output 2
    # The numbers are: 5(idx1), 7(idx2), 4(idx3), 4(idx4), 6(idx5), 8(idx6)
    # Largest is 8, second largest is 7, which is at index 2.
    # So we need to find the second largest distinct value's index? Or second largest element?
    # If there were duplicates of the largest, what happens?
    # Let's think: "second largest number" typically means the second largest distinct value.
    # Find second largest distinct value, then find its index (first occurrence or any?).
    # Usually index means the position. Let's find what makes sense with sample.
    
    # Method: Get distinct values, sort descending, take second. Find its index in original array.
    # But what if second largest appears multiple times? Typically we'd take the first occurrence.
    
    distinct = sorted(set(arr), reverse=True)
    if len(distinct) < 2:
        # If all elements are the same, there's no second largest. Output?
        # Problem doesn't specify. Assume there are at least 2 distinct values or handle appropriately.
        # Let's just print -1 or something? But constraint 0<n<100.
        print(0)
        return
    
    second_largest = distinct[1]
    
    # Find the first index (1-based) where second_largest appears
    for i in range(n):
        if arr[i] == second_largest:
            print(i + 1)
            return

if __name__ == '__main__':
    main()
