import sys

def sum_proper_divisors(n):
    if n <= 1:
        return 0
    total = 1
    i = 2
    while i * i <= n:
        if n % i == 0:
            total += i
            if i != n // i:
                total += n // i
        i += 1
    return total

def find_ideal_pair(n):
    s = sum_proper_divisors(n)
    if s != n and sum_proper_divisors(s) == n:
        return s
    return -1

def main():
    data = sys.stdin.read().strip()
    if not data:
        print(-1)
        return
    try:
        n = int(data)
        result = find_ideal_pair(n)
        print(result)
    except ValueError:
        print(-1)

if __name__ == "__main__":
    main()
