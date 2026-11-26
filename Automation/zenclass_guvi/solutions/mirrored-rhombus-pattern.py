import sys

def main():
    n = int(sys.stdin.readline().strip())
    if n <= 0:
        return
    for i in range(n):
        print(' ' * i + '*' * n)

if __name__ == "__main__":
    main()
