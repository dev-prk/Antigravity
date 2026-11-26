import sys
import math

s, x = sys.stdin.read().split()
if math.gcd(len(s), len(x)) == 1:
    print("yes")
else:
    print("no")
