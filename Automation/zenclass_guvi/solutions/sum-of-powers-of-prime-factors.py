import sys
import math

def sum_of_powers_of_prime_factors(n):
    if n <= 1:
        return 0
    
    total = 0
    
    # Handle factor 2
    if n % 2 == 0:
        count = 0
        while n % 2 == 0:
            n //= 2
            count += 1
        total += count
    
    # Handle odd factors
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            count = 0
            while n % i == 0:
                n //= i
                count += 1
            total += count
    
    # If n is still greater than 1, then it's a prime factor
    if n > 1:
        total += 1
    
    return total

def main():
    n = int(sys.stdin.readline().strip())
    print(sum_of_powers_of_prime_factors(n))

if __name__ == "__main__":
    main()
