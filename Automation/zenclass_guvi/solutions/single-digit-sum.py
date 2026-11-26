import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        print(0)
    else:
        n = abs(n)
        dr = 1 + (n - 1) % 9
        print(dr)

if __name__ == "__main__":
    main()
