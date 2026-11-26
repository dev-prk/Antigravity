import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    if n <= 0:
        print(0)
        return
    arr = []
    for i in range(1, min(n, len(data) - 1) + 1):
        arr.append(int(data[i]))
    
    # Build a set for O(1) lookup
    arr_set = set(arr)
    
    count = 0
    for i in range(n):
        # Position I: the problem says "I is the position of the element"
        # From the test case: N=6, array=[6, -1, 2, 36, 12, -3]
        # Let's figure out which positions are 1-indexed or 0-indexed
        # If I is 1-indexed: N*I = 6*I
        #   I=1: 6*1=6 -> present (arr[0]=6) ✓
        #   I=2: 6*2=12 -> present (arr[4]=12) ✓
        #   I=3: 6*3=18 -> not present
        #   I=4: 6*4=24 -> not present
        #   I=5: 6*5=30 -> not present
        #   I=6: 6*6=36 -> present (arr[3]=36) ✓
        # That gives 3 lucky numbers: at positions 1, 2, 6 (1-indexed)
        # Output is 3. So I is 1-indexed.
        
        I = i + 1  # 1-indexed position
        target = n * I
        if target in arr_set:
            count += 1
    
    print(count)

if __name__ == "__main__":
    main()
