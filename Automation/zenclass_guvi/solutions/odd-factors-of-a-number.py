import sys

def main():
    n = int(sys.stdin.readline().strip())
    factors = []
    for i in range(1, n + 1, 2):
        if n % i == 0:
            factors.append(str(i))
    print(' '.join(factors))

if __name__ == "__main__":
    main()
