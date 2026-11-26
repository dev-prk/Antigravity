import sys
import math

def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.isqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

data = sys.stdin.read().strip()
if data:
    try:
        n = int(data)
        print("PRIME" if is_prime(n) else "NOT PRIME")
    except ValueError:
        pass
