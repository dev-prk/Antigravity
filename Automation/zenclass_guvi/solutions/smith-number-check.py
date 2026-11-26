import sys

def digit_sum(n):
    return sum(ord(ch) - 48 for ch in str(n))

def is_prime(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True

def is_smith(n):
    if n <= 1 or is_prime(n):
        return False

    target = digit_sum(n)
    factor_sum = 0
    temp = n
    p = 2

    while p * p <= temp:
        while temp % p == 0:
            factor_sum += digit_sum(p)
            temp //= p
        p = 3 if p == 2 else p + 2

    if temp > 1:
        factor_sum += digit_sum(temp)

    return factor_sum == target

data = sys.stdin.read().strip()
if data:
    n = int(data.split()[0])
    print("Yes" if is_smith(n) else "No")
else:
    print("No")
