import sys
import math

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    if n <= 0:
        print(0)
        return
    # A bucket i is filled at the end if it has an odd number of divisors.
    # Numbers with an odd number of divisors are perfect squares.
    # So the answer is the count of perfect squares <= n, which is floor(sqrt(n)).
    print(math.isqrt(n))

if __name__ == "__main__":
    main()
