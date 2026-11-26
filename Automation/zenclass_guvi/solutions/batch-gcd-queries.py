import sys
import math
import ast

data = sys.stdin.read().strip()
pairs = ast.literal_eval(data)
for a, b in pairs:
    print(math.gcd(a, b))
