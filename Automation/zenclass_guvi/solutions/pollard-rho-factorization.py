import sys
import random
import math

def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    # Miller-Rabin primality test
    d = n - 1
    r = 0
    while d % 2 == 0:
        r += 1
        d //= 2
    
    witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    
    for a in witnesses:
        if a >= n:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def pollard_rho(n):
    if n % 2 == 0:
        return 2
    
    while True:
        if n % 2 == 0:
            return 2
        
        c = random.randint(1, n - 1)
        f = lambda x: (x * x + c) % n
        x, y, d = 2, 2, 1
        
        while d == 1:
            x = f(x)
            y = f(f(y))
            d = math.gcd(abs(x - y), n)
        
        if d != n:
            return d

def factorize(n):
    if n <= 1:
        return []
    if is_prime(n):
        return [n]
    
    factors = []
    stack = [n]
    
    while stack:
        num = stack.pop()
        if num <= 1:
            continue
        if is_prime(num):
            factors.append(num)
        else:
            d = pollard_rho(num)
            stack.append(d)
            stack.append(num // d)
    
    factors.sort()
    return factors

def main():
    line = sys.stdin.readline().strip()
    
    # Parse input like "n=8051"
    if '=' in line:
        n = int(line.split('=')[1])
    else:
        n = int(line)
    
    result = factorize(n)
    print(str(result).replace(' ', ''))

if __name__ == "__main__":
    main()
