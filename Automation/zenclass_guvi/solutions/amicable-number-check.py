import sys
import math

def sum_proper_divisors(n: int) -> int:
    if n <= 1:
        return 0
    total = 0
    root = int(math.isqrt(n))
    for i in range(1, root + 1):
        if n % i == 0:
            total += i
            j = n // i
            if j != i:
                total += j
    return total - n  # exclude n itself

def main() -> None:
    data = sys.stdin.read().strip().split()
    if len(data) < 2:
        print("No")
        return
    try:
        a = int(data[0])
        b = int(data[1])
    except ValueError:
        print("No")
        return

    if a <= 0 or b <= 0 or a == b:
        print("No")
        return

    sum_a = sum_proper_divisors(a)
    sum_b = sum_proper_divisors(b)

    print("Yes" if sum_a == b and sum_b == a else "No")

if __name__ == "__main__":
    main()
