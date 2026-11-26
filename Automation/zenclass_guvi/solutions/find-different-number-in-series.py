def solve():
    n = int(input().strip())
    arr = list(map(int, input().split()))
    
    if n == 0:
        print(-1)
        return
    
    if n == 1:
        print(-1)
        return
    
    even_count = 0
    odd_count = 0
    
    for num in arr:
        if num % 2 == 0:
            even_count += 1
        else:
            odd_count += 1
    
    if even_count == 1:
        for num in arr:
            if num % 2 == 0:
                print(num)
                return
    elif odd_count == 1:
        for num in arr:
            if num % 2 != 0:
                print(num)
                return
    else:
        print(-1)

solve()
