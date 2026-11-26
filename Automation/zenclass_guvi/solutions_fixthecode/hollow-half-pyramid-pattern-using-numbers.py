n = int(input())
for i in range(1, n+1):
    if i == 1:
        print(1)
    elif i == n:
        print(''.join(str(j) for j in range(1, i+1)))
    else:
        print('1' + ' '*(i-2) + str(i))
