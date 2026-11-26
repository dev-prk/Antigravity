import math

n = int(input())
k = 1 << int(math.log2(n))
print(n - k)
