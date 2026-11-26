n = int(input())
if n <= 1:
    print("no")
else:
    is_divisible = False
    for i in range(2, n):
        if n % i == 0:
            is_divisible = True
            break
    if is_divisible:
        print("yes")
    else:
        print("no")
