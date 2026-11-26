import sys

def sieve(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = False
    return is_prime

def main():
    n = int(sys.stdin.readline().strip())
    if n < 2:
        print(0)
        return
    
    max_val = n
    is_prime = sieve(max_val)
    
    count = 0
    for i in range(2, n // 2 + 1):
        if is_prime[i] and is_prime[n - i]:
            count += 1
    
    print(count)

if __name__ == "__main__":
    main()
