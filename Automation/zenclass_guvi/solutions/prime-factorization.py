import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return

    n = int(data[0])
    if n < 0:
        n = -n

    factors = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            factors.append(d)
            while n % d == 0:
                n //= d
        d += 1 if d == 2 else 2

    if n > 1:
        factors.append(n)

    print(' '.join(map(str, factors)))

if __name__ == '__main__':
    main()
