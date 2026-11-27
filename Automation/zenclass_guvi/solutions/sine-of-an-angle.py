import math

A = int(input().strip())
result = math.sin(math.radians(A))

rounded = round(result, 10)
if rounded == int(rounded):
    print(int(rounded))
else:
    if rounded == 0:
        print(0)
    else:
        print(rounded)
