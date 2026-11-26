import sys
import math

def main():
    line = sys.stdin.readline().strip()
    if '=' in line:
        n = int(line.split('=')[1])
    else:
        n = int(line)
    
    if n < 2:
        print('[]')
        return
    
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    
    for i in range(2, int(math.sqrt(n)) + 1):
        if sieve[i]:
            for j in range(i * i, n + 1, i):
                sieve[j] = False
    
    primes = [i for i in range(2, n + 1) if sieve[i]]
    print('[' + ','.join(map(str, primes)) + ']')

if __name__ == "__main__":
    main()
