def sum_recursive(n):
    if n == 1:
        return 1
    return n + sum_recursive(n - 1)

n = int(input())
print(sum_recursive(n))
