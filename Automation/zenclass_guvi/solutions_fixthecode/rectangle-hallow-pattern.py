n, m = map(int, input().split())
for i in range(n):
    if i == 0 or i == n - 1:
        print(' '.join(['*'] * m))
    else:
        print('*' + ' ' * (2 * m - 3) + '*')
