s = input()
L1, L2 = [], []
for c in s:
    if c in L1:
        if c not in L2:
            L2.append(c)
    else:
        L1.append(c)
if L2:
    print(*L2)
else:
    print(-1)
