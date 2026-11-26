import sys
import math

data = sys.stdin.read().strip().split()
if len(data) >= 2:
    a, b = int(data[0]), int(data[1])
    lcm = abs(a * b) // math.gcd(a, b)
    print(lcm)
