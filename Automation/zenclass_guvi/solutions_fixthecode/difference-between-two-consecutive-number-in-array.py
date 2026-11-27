n, m = map(int, input().split())
l = list(map(int, input().split()))
result = []
for i in range(n):
    diff = abs(l[i] - l[(i + 1) % n])
    if diff > m:
        result.append('1')
    else:
        result.append('0')
print(' '.join(result))
