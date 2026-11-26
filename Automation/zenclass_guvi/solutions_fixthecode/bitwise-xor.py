n=int(input())
l=list(map(int,input().split()))
res=0
for i in range(n):
    res=res^l[i]
print(res)
