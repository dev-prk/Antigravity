def solution():
    R = int(input().strip())
    for i in range(R):
        spaces = ' ' * (R - i - 1)
        if i == 0:
            print(spaces + '*')
        elif i == R - 1:
            stars = '* ' * (R - 1) + '*'
            print(spaces + stars)
        else:
            inner_spaces = 2 * i - 1
            print(spaces + '*' + ' ' * inner_spaces + '*')

solution()
