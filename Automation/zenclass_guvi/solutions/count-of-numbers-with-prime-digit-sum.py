import sys

def is_prime(n):
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def main():
    data = sys.stdin.read().split()
    if len(data) < 2:
        return
    L = int(data[0])
    R = int(data[1])
    
    # Count numbers in [L, R) with prime digit sum
    # R is exclusive
    
    def count_prime_digit_sum(n):
        """Count numbers in [0, n) with prime digit sum."""
        if n <= 0:
            return 0
        count = 0
        for num in range(1, n):
            s = 0
            temp = num
            while temp > 0:
                s += temp % 10
                temp //= 10
            if is_prime(s):
                count += 1
        return count
    
    # We need count in [L, R) = count([0, R)) - count([0, L))
    result = count_prime_digit_sum(R) - count_prime_digit_sum(L)
    print(result)

main()
