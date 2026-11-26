import sys
import math

a = float(sys.stdin.read().strip())
area = (math.sqrt(3) * a * a) / 4
print(f"{area:.2f}")
