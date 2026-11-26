n = int(input())
l = list(map(int, input().split()))
result = []

for i in range(len(l)):
    found = False
    for j in range(i + 1, len(l)):
        if l[j] < l[i]:
            result.append(l[j])
            found = True
            break
    if not found:
        result.append(-1)

print(' '.join(map(str, result)))
