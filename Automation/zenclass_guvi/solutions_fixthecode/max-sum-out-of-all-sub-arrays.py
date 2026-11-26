size = int(input())
a = list(map(int, input().split()))
maxsubar = a[0]
curr_max = a[0]
for i in range(1, size):
    curr_max = max(a[i], curr_max + a[i])
    maxsubar = max(maxsubar, curr_max)
    
print(maxsubar)
