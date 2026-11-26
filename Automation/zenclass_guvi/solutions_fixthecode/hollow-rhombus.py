a = int(input())
for i in range(a):
    leading = ' ' * (a - 1 - i)
    if i == 0 or i == a - 1:
        middle = '*' * a
    else:
        middle = '*' + ' ' * (a - 2) + '*'
    print(leading + middle)
