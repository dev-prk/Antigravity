n = int(input())
l = list(map(int, input().split()))
flag = 0
for i in range(len(l) - 1):
    val = l[i]
    times = l[i + 1]
    count = l.count(val)
    if times == count:
        flag += 1
print(flag)
