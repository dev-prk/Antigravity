import sys

def is_prime(x):
    if x < 2:
        return False
    if x == 2:
        return True
    if x % 2 == 0:
        return False
    i = 3
    while i * i <= x:
        if x % i == 0:
            return False
        i += 2
    return True

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    n = int(data)
    primes = []
    candidate = n + 1
    while len(primes) < 3:
        if is_prime(candidate):
            primes.append(candidate)
        candidate += 1
    print(' '.join(map(str, primes)))

if __name__ == "__main__":
    main()
