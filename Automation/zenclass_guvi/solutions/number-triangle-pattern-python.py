n = int(input())
for i in range(1, n + 1):
    print(''.join(str(j) for j in range(1, i + 1)))
