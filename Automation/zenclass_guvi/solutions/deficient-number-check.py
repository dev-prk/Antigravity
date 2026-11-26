import sys
import math

def main():
    data = sys.stdin.read().split()
    if not data:
        return

    n = int(data[0])

    if n <= 0:
        print("No")
        return

    if n == 1:
        print("Yes")
        return

    total = 1
    root = math.isqrt(n)

    for i in range(2, root + 1):
        if n % i == 0:
            total += i
            other = n // i
            if other != i:
                total += other

    print("Yes" if total < n else "No")

if __name__ == "__main__":
    main()
