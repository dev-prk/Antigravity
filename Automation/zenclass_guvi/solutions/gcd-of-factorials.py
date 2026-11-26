import sys
import math

data = sys.stdin.read().strip().split()
if len(data) < 2:
    print(0)
else:
    A = int(data[0])
    B = int(data[1])
    
    if A < 0 or B < 0:
        print(1)
    elif A == 0 or B == 0:
        print(1)
    else:
        min_val = min(A, B)
        result = math.factorial(min_val)
        print(result)
