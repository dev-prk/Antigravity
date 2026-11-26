n, k = map(int, input().split())
lt = list(map(int, input().split()))
found = -1
for i in range(n):
    if lt[i] <= k:
        found = i
if found != -1:
    print(found)
else:
    print(-1)
