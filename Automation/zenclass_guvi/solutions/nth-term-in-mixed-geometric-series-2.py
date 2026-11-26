import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    n = int(data)
    # Odd terms (1,3,5,7,...) form geometric series: 1, 2, 4, 8, ... which is 2^(k-1) for k-th odd term
    # Term position n:
    # If n is odd: it is the (n+1)//2 -th term in the first geometric series (powers of 2: 2^0, 2^1, ...)
    #   term = 2^((n+1)//2 - 1) = 2^((n-1)//2)
    # If n is even: it is the n//2 -th term in the second geometric series (powers of 3: 3^0, 3^1, ...)
    #   term = 3^(n//2 - 1)
    if n % 2 == 1:
        result = 1 << ((n - 1) // 2)  # 2^((n-1)//2)
    else:
        result = 3 ** (n // 2 - 1)
    print(result)

if __name__ == "__main__":
    main()
