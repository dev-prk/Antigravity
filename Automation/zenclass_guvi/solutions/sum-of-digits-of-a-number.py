import sys

def main():
    line = sys.stdin.readline()
    if not line:
        return
    n = int(line.strip())
    n = abs(n)
    s = 0
    while n:
        s += n % 10
        n //= 10
    print(s)

if __name__ == "__main__":
    main()
