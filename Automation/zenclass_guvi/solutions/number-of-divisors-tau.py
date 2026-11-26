import sys
import math

def tau(n):
    if n == 0:
        return 0
    if n < 0:
        n = -n
    if n == 1:
        return 1
    count = 0
    sqrt_n = int(math.isqrt(n))
    for i in range(1, sqrt_n + 1):
        if n % i == 0:
            if i * i == n:
                count += 1
            else:
                count += 2
    return count

def main():
    line = sys.stdin.readline().strip()
    if '=' in line:
        line = line.split('=')[1]
    n = int(line)
    print(tau(n))

if __name__ == "__main__":
    main()
