import sys, math

def main():
    data = sys.stdin.read().strip()
    if data:
        n = int(data)
        print(math.isqrt(n))

if __name__ == "__main__":
    main()
