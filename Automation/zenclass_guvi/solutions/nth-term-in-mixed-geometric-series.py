def solve():
    n = int(input().strip())
    if n % 2 == 1:
        k = (n + 1) // 2
        result = 2 ** (k - 1)
    else:
        k = n // 2
        result = 3 ** (k - 1)
    print(result)

solve()
