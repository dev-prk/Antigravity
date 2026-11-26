def solve():
    n = int(input().strip())
    if n == 0:
        print(0)
        return
    arr = list(map(int, input().split()))
    
    max_sum = float('-inf')
    current_sum = arr[0]
    
    for i in range(1, n):
        if arr[i] > arr[i-1]:
            current_sum += arr[i]
        else:
            current_sum = arr[i]
        max_sum = max(max_sum, current_sum)
    
    max_sum = max(max_sum, arr[0])
    
    print(max_sum)

solve()
