import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        print(0)
        return
    arr = list(map(int, data[1:1+n]))
    
    # Handle edge case of N=0 (though constraints say N>=1, handle anyway)
    if not arr:
        print(0)
        return
    
    # Initialize max and min product with first element
    max_prod = arr[0]
    min_prod = arr[0]
    result = arr[0]
    
    for i in range(1, n):
        # If current is 0, reset max and min to 0
        if arr[i] == 0:
            max_prod = 1
            min_prod = 1
            continue
        
        # Save old values since we update them in place
        old_max = max_prod
        old_min = min_prod
        
        # Calculate new max and min products
        max_prod = max(arr[i], max_prod * arr[i], min_prod * arr[i])
        min_prod = min(arr[i], max_prod * arr[i] if False else old_max * arr[i], old_min * arr[i])
        
        # Update global result
        if max_prod > result:
            result = max_prod
    
    print(result)

if __name__ == "__main__":
    main()
