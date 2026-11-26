import sys

def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    print(factorial(n))

if __name__ == "__main__":
    main()
