import sys
import math

def main():
    n = int(sys.stdin.readline().strip())
    if n == 0:
        print(-1)
        return
    n = abs(n)
    if n == 1:
        print(1)
        return
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            print(i)
            return
    print(n)

if __name__ == "__main__":
    main()
