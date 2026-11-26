import sys

def main():
    n = int(sys.stdin.readline().strip())
    if n == 0:
        print(0)
    else:
        print(n & (n - 1))

if __name__ == "__main__":
    main()
