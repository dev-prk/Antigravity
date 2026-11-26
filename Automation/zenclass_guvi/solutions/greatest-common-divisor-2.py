import sys
import math

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    k = int(data[1]) if len(data) > 1 else 0
    print(math.gcd(n, k))

if __name__ == "__main__":
    main()
