import sys
import math

data = sys.stdin.read().strip()
if not data:
    print(0)
else:
    if '=' in data and ',' in data:
        parts = data.replace('a=', '').replace('b=', '').split(',')
        a = int(parts[0].strip())
        b = int(parts[1].strip())
        print(math.gcd(a, b))
    else:
        nums = list(map(int, data.split()))
        print(math.gcd(nums[0], nums[1]))
