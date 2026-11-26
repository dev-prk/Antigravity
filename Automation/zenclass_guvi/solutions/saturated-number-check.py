import sys

def is_saturated(n):
    s = str(n)
    unique_digits = set(s)
    return len(unique_digits) == 2

n = sys.stdin.readline().strip()
if is_saturated(n):
    print("Saturated")
else:
    print("Unsaturated")
