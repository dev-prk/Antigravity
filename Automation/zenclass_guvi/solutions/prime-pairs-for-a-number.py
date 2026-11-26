import sys
import math

def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

def main():
    n = int(sys.stdin.readline().strip())
    pairs = []
    for p in range(2, int(math.sqrt(n)) + 1):
        if n % p == 0:
            q = n // p
            if is_prime(p) and is_prime(q):
                pairs.append((max(p, q), min(p, q)))
    pairs.sort(reverse=True)
    if not pairs:
        print(-1)
    else:
        for pair in pairs:
            print(pair[0], pair[1])

if __name__ == "__main__":
    main()
