import sys

MOD = 10**9 + 7

def main():
    N = int(sys.stdin.readline().strip())
    # The sequence is: 2, 6, 11, 17, 24, ...
    # Differences: 4, 5, 6, 7, ...
    # a(1) = 2
    # a(n) = a(n-1) + (n+2) for n >= 2
    # a(n) = 2 + sum(i=2 to n) (i+2) = 2 + sum(i=2 to n) i + 2*(n-1)
    #      = 2 + (n(n+1)/2 - 1) + 2n - 2
    #      = 1 + n(n+1)/2 + 2n - 2
    #      = n(n+1)/2 + 2n - 1
    #      = n(n+1)/2 + 2n - 1
    #      = n(n+1)/2 + (4n - 2)/2
    #      = (n(n+1) + 4n - 2)/2
    #      = (n² + n + 4n - 2)/2
    #      = (n² + 5n - 2)/2
    # Let's verify: n=5: (25 + 25 - 2)/2 = 48/2 = 24 ✓
    # n=19: (361 + 95 - 2)/2 = 454/2 = 227 ✓
    result = (N * N + 5 * N - 2) // 2
    result = result % MOD
    print(result)

if __name__ == "__main__":
    main()
