n, k = map(int, input().split())
l = list(map(int, input().split()))
r = []
for i in range(len(l) - k + 1):
    window = l[i:i+k]
    if 0 in window:
        r.append(window.index(0) + 1 + i)
    else:
        r.append(-1)
print(*r)
