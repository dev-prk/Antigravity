import sys

def gcd(a, b):
    a = abs(a)
    b = abs(b)
    while b:
        a, b = b, a % b
    return a

def main():
    data = sys.stdin.read().split()
    if len(data) < 2:
        return
    a = int(data[0])
    b = int(data[1])
    print(gcd(a, b))

if __name__ == "__main__":
    main()
