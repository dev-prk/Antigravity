import sys

def main():
    n = int(sys.stdin.readline().strip())
    if n == 0:
        print(0)
        return
    if n < 0:
        n = -n
    digits = []
    while n > 0:
        digits.append(str(n % 10))
        n //= 10
    digits.reverse()
    print(' '.join(digits))

if __name__ == "__main__":
    main()
