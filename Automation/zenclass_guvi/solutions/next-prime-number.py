import sys


def is_prime(x):
    if x < 2:
        return False
    if x == 2:
        return True
    if x % 2 == 0:
        return False
    i = 3
    while i * i <= x:
        if x % i == 0:
            return False
        i += 2
    return True


def next_prime(n):
    if n < 2:
        return 2
    m = n + 1
    while not is_prime(m):
        m += 1
    return m


def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    n = int(data)
    print(next_prime(n))


if __name__ == "__main__":
    main()
