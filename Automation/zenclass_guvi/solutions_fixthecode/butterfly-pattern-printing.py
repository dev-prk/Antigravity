n = int(input())
for i in range(1, n + 1):
    left = '*' * i
    spaces = ' ' * (2 * n - 2 * i)
    right = '*' * i
    print(left + spaces + right)
for i in range(n, 0, -1):
    left = '*' * i
    spaces = ' ' * (2 * n - 2 * i)
    right = '*' * i
    print(left + spaces + right)
