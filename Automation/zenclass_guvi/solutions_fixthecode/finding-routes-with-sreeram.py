n = int(input())
d = {}
l = []
c = []
for i in range(n):
    (a, b) = map(str, input().split())
    d[a] = b
    l.append(a)
    c.append(a)
    c.append(b)

# Find starting point: the X that doesn't appear in Ys (not in c list except as itself)
from collections import Counter
counts = Counter(c)
for i in l:
    if counts[i] == 1:
        p1 = i
        break

for i in range(n):
    print(p1, "to", d[p1])
    p1 = d[p1]
