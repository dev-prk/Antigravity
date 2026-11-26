import sys

def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    arr = list(map(int, data[1:n+1]))
    arr.sort()
    
    # The minimum number in the list
    minimum = arr[0]
    
    # Find the smallest missing non-sum number
    # Start checking from the minimum + 1
    m = minimum + 1
    
    # Generate all possible subset sums up to some reasonable limit
    # We need to find all sums that can be formed by any subset
    
    # Use dynamic programming to find reachable sums
    max_sum = sum(arr) + 1
    reachable = [False] * (max_sum + 1)
    reachable[0] = True
    
    for num in arr:
        for s in range(max_sum, num - 1, -1):
            if reachable[s - num]:
                reachable[s] = True
    
    # Now find the smallest m > minimum such that:
    # 1. m is not in arr
    # 2. m is not reachable as a subset sum
    
    arr_set = set(arr)
    
    while True:
        if m not in arr_set and not reachable[m]:
            print(m)
            return
        m += 1

if __name__ == "__main__":
    main()
