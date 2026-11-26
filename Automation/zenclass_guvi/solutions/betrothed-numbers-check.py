import sys
import math

def sum_proper_divisors(n):
    if n <= 1:
        return 0
    total = 1  # 1 is always a proper divisor for n > 1
    i = 2
    while i * i <= n:
        if n % i == 0:
            total += i
            if i != n // i:
                total += n // i
        i += 1
    return total

def main():
    data = sys.stdin.read().strip().split()
    if len(data) < 2:
        print("No")
        return
    a = int(data[0])
    b = int(data[1])
    if a <= 0 or b <= 0:
        print("No")
        return
    sa = sum_proper_divisors(a)
    sb = sum_proper_divisors(b)
    if sa == b + 1 and sb == a + 1:
        print("Yes")
    else:
        print("No")

if __name__ == "__main__":
    main()
