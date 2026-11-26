import sys

def main():
    # Read input
    data = sys.stdin.read().strip().split()
    a = int(data[0])
    b = int(data[1])
    
    # Generate primes up to 17 (maximum number of 1's in binary for numbers up to 100000)
    # 100000 in binary is 11000011010100000, which has at most 17 ones
    max_ones = 17
    is_prime = [True] * (max_ones + 1)
    is_prime[0] = is_prime[1] = False
    
    for i in range(2, int(max_ones**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, max_ones + 1, i):
                is_prime[j] = False
    
    # Count numbers with prime number of 1's in binary
    count = 0
    for num in range(a, b + 1):
        ones = bin(num).count('1')
        if ones <= max_ones and is_prime[ones]:
            count += 1
    
    print(count)

if __name__ == "__main__":
    main()
