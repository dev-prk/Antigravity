n = int(input())
a = []
for _ in range(n):
    a.append(input())
k = int(input())
for _ in range(k):
    p = input()
    l = []
    for word in a:
        if word.startswith(p):
            l.append(word)
    if len(l) == 0:
        print(p)
    elif len(l) == 1:
        print(l[0])
    else:
        l.sort()
        print(l[0] + '+')
