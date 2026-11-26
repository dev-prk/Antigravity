import sys
import math
import re

def egcd(a, b):
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = egcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)

def modinv(a, m):
    # returns x such that a*x % m == 1, assuming gcd(a,m)=1, m>0
    g, x, y = egcd(a % m, m)
    # g should be 1
    return x % m

def solve():
    data = sys.stdin.read()
    nums = list(map(int, re.findall(r'-?\d+', data)))
    if len(nums) < 3:
        # maybe not enough input
        return
    a, b, m = nums[0], nums[1], nums[2]
    
    if m == 0:
        # ax = b over integers
        if a == 0:
            print(0 if b == 0 else -1)
        else:
            if b % a == 0:
                print(b // a)
            else:
                print(-1)
        return
    
    # normalize modulus to positive
    m_abs = abs(m)
    a_mod = a % m_abs
    b_mod = b % m_abs
    
    if a_mod == 0:
        if b_mod == 0:
            print(0)
        else:
            print(-1)
        return
    
    g = math.gcd(a_mod, m_abs)
    if b_mod % g != 0:
        print(-1)
        return
    
    a_red = a_mod // g
    b_red = b_mod // g
    m_red = m_abs // g
    
    inv = modinv(a_red, m_red)
    x = (b_red * inv) % m_red
    print(x)

if __name__ == '__main__':
    solve()
