import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return

    n = int(data[0])

    if n <= 1:
        print("No")
        return

    total = 1
    i = 2

    while i * i <= n:
        if n % i == 0:
            total += i
            j = n // i
            if j != i:
                total += j
        i += 1

    print("Yes" if total > n else "No")

if __name__ == "__main__":
    main()
