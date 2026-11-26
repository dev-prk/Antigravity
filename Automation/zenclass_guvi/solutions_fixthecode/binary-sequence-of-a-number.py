n = int(input())
ans = []
for i in range(1, n+1):
    ans.append(bin(i)[2:])
print(*ans)
