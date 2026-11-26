import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return

    n = int(data)

    if n <= 1:
        print("No")
        return

    total = 1
    i = 2

    while i * i <= n:
        if n % i == 0:
            total += i
            other = n // i
            if other != i:
                total += other
        i += 1

    print("Yes" if total == n else "No")

main()
