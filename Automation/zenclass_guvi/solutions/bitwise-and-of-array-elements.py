import sys

data = sys.stdin.read().split()
if not data:
    sys.exit()
n = int(data[0])
if n == 0:
    print(0)
    sys.exit()
arr = list(map(int, data[1:1+n]))
res = arr[0]
for i in range(1, n):
    res &= arr[i]
print(res)
