n = int(input())
l = [int(x) for x in input().split()]
for i in range(n):
    minind = i
    for j in range(i + 1, n):
        if l[j] < l[minind]:
            minind = j
    if minind != i:
        l[i], l[minind] = l[minind], l[i]
    print(*l)
