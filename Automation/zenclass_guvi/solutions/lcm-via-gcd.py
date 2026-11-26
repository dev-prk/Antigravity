import sys
import math

data = sys.stdin.read().strip()
parts = data.split(',')
a_part = parts[0].split('=')[1]
b_part = parts[1].split('=')[1].rstrip(')')

a = int(a_part)
b = int(b_part)

result = (a * b) // math.gcd(a, b)
print(result)
