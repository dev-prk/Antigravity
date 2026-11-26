import sys

def mobius_sieve(N):
    if N < 0:
        return [0]
    mu = [1] * (N + 1)
    mu[0] = 0
    is_prime = [True] * (N + 1)
    primes = []
    for i in range(2, N + 1):
        if is_prime[i]:
            primes.append(i)
            mu[i] = -1
        for p in primes:
            if i * p > N:
                break
            is_prime[i * p] = False
            if i % p == 0:
                mu[i * p] = 0
                break
            else:
                mu[i * p] = -mu[i]
    return mu

def main():
    line = sys.stdin.readline().strip()
    if '=' in line:
        line = line.split('=')[1]
    N = int(line)
    result = mobius_sieve(N)
    print(result)

if __name__ == "__main__":
    main()
