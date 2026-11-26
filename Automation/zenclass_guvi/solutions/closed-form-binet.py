import sys
import math

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    n = None
    for line in data.splitlines():
        line = line.strip()
        if not line:
            continue
        if '=' in line:
            val = line.split('=', 1)[1].strip()
        else:
            val = line
        try:
            n = int(val)
        except ValueError:
            continue
        break

    if n is None or n < 0:
        print(0)
        return

    if n <= 0:
        print(0)
        return

    phi = (1 + math.sqrt(5)) / 2
    psi = (1 - math.sqrt(5)) / 2
    fib = (phi ** n - psi ** n) / math.sqrt(5)
    print(int(round(fib)))

if __name__ == "__main__":
    main()
