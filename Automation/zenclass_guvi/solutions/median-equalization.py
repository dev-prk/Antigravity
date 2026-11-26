import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    arr = list(map(int, data[1:1+n]))
    k = int(data[1+n]) if 1+n < len(data) else 0
    
    arr.sort()
    
    def get_median(arr):
        m = len(arr)
        if m % 2 == 1:
            return arr[m // 2]
        else:
            return (arr[m // 2 - 1] + arr[m // 2]) / 2
    
    cur_med = get_median(arr)
    
    if cur_med == k:
        print(0)
        return
    
    count = 0
    
    # We can add k elements. We need to find minimum number of k's to add so that median becomes k.
    
    # Strategy: 
    # If current median < k, we need to increase median by adding k's.
    # If current median > k, we need to decrease median by adding k's.
    
    # Since we're only adding k, let's simulate.
    
    # But n can be large. Let's think mathematically.
    
    # Let's binary search on the number of elements to add.
    
    lo, hi = 0, n + 1
    # hi = n is probably enough since adding more than n elements of k will certainly make median k or closer.
    # But to be safe, let's use n * 2.
    hi = n * 2 + 10
    
    def check(cnt):
        # Add cnt copies of k to arr and compute median.
        new_arr = arr + [k] * cnt
        new_arr.sort()
        m = len(new_arr)
        if m % 2 == 1:
            return new_arr[m // 2] == k
        else:
            return (new_arr[m // 2 - 1] + new_arr[m // 2]) / 2 == k
    
    # Binary search for minimum cnt such that median becomes k
    # But is median as function of cnt monotonic? Let's think.
    # As we add more k's:
    # - If k is larger than current median, median increases towards k.
    # - If k is smaller than current median, median decreases towards k.
    
    # So median approaches k as cnt -> infinity.
    
    # Let's just linear scan from 0 upward, but with a bound.
    # Actually, the max elements needed is at most n (or some small multiple).
    
    for cnt in range(0, n * 2 + 20):
        new_arr = arr + [k] * cnt
        new_arr.sort()
        m = len(new_arr)
        if m % 2 == 1:
            med = new_arr[m // 2]
        else:
            med = (new_arr[m // 2 - 1] + new_arr[m // 2]) / 2
        
        if med == k:
            print(cnt)
            return
        # Check if median will ever reach k
        # If med and k have same relationship and are moving away, break (shouldn't happen)
    
    # If we didn't find, try larger
    for cnt in range(n * 2 + 20, n * 10 + 100):
        new_arr = arr + [k] * cnt
        new_arr.sort()
        m = len(new_arr)
        if m % 2 == 1:
            med = new_arr[m // 2]
        else:
            med = (new_arr[m // 2 - 1] + new_arr[m // 2]) / 2
        
        if med == k:
            print(cnt)
            return
    
    print(0)

if __name__ == "__main__":
    main()
