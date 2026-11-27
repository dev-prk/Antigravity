import math
n = int(input())
sr = math.sqrt(n)
c = sr - math.floor(sr)
if c == 0:
    print("yes")
else:
    print("no")
