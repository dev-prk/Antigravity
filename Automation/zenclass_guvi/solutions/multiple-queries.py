import sys

def pow_mod(a, b, m):
    if m == 1:
        return 0
    result = 1
    a = a % m
    while b > 0:
        if b % 2 == 1:
            result = (result * a) % m
        b = b >> 1
        a = (a * a) % m
    return result

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        line = line.strip('()')
        parts = line.split(',')
        if len(parts) != 3:
            continue
        try:
            a = int(parts[0].strip())
            b = int(parts[1].strip())
            m = int(parts[2].strip())
            result = pow_mod(a, b, m)
            print(result)
        except ValueError:
            continue

if __name__ == "__main__":
    main()
