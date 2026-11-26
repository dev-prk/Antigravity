import sys

def main():
    data = sys.stdin.readline()
    if not data:
        print(-1)
        return

    try:
        n = int(data.strip())
    except ValueError:
        print(-1)
        return

    even_factors = [str(i) for i in range(2, n + 1, 2) if n % i == 0]

    if even_factors:
        print(" ".join(even_factors))
    else:
        print(-1)

if __name__ == "__main__":
    main()
