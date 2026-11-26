import sys
import math

def prime_factors(n):
    factors = []
    while n % 2 == 0:
        factors.append(2)
        n //= 2
    i = 3
    while i * i <= n:
        while n % i == 0:
            factors.append(i)
            n //= i
        i += 2
    if n > 1:
        factors.append(n)
    return sorted(set(factors))

def main():
    n = int(sys.stdin.readline().strip())
    factors = prime_factors(n)
    print(' '.join(map(str, factors)))

if __name__ == "__main__":
    main()
