import sys

def main():
    n = int(sys.stdin.readline().strip())
    if n == 0:
        print(1)
    elif n == 1:
        print(1)
    else:
        a, b = 1, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        print(b)

if __name__ == "__main__":
    main()
