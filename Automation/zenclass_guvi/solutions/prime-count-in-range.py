import sys
import math

def main():
    # Read all input at once
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    q = int(data[0])
    
    if q == 0:
        return
    
    queries = []
    max_r = 0
    idx = 1
    
    for i in range(q):
        l = int(data[idx])
        r = int(data[idx + 1])
        queries.append((l, r))
        if r > max_r:
            max_r = r
        idx += 2
    
    # Handle edge case where max_r < 2
    if max_r < 2:
        for _ in queries:
            print(0)
        return
    
    # Sieve of Eratosthenes
    is_prime = [True] * (max_r + 1)
    is_prime[0] = False
    is_prime[1] = False
    
    for i in range(2, int(math.sqrt(max_r)) + 1):
        if is_prime[i]:
            for j in range(i * i, max_r + 1, i):
                is_prime[j] = False
    
    # Build prefix sum of primes
    prime_count = [0] * (max_r + 1)
    count = 0
    for i in range(max_r + 1):
        if is_prime[i]:
            count += 1
        prime_count[i] = count
    
    # Process queries
    results = []
    for l, r in queries:
        if l > r:
            results.append(0)
        elif r < 2:
            results.append(0)
        elif l <= 2:
            results.append(prime_count[r])
        else:
            results.append(prime_count[r] - prime_count[l - 1])
    
    # Output results
    for res in results:
        print(res)

if __name__ == "__main__":
    main()
