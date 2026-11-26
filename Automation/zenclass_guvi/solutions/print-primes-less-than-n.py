import sys
import math

def main():
    line = sys.stdin.readline()
    if not line:
        return
    n = int(line.strip())
    
    if n <= 2:
        return
    
    sieve = [True] * n
    sieve[0] = False
    sieve[1] = False
    
    for i in range(2, int(math.sqrt(n)) + 1):
        if sieve[i]:
            for j in range(i * i, n, i):
                sieve[j] = False
    
    primes = []
    for i in range(2, n):
        if sieve[i]:
            primes.append(str(i))
    
    print(' '.join(primes))

if __name__ == "__main__":
    main()
