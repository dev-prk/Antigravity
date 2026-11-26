import sys
from math import gcd

def lcm(a, b):
    return a // gcd(a, b) * b

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        print(0)
        return
    nums = list(map(int, data[1:1+n]))
    result = 1
    for num in nums:
        result = lcm(result, num)
    print(result)

main()
