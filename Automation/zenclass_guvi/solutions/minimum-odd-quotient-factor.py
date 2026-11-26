import sys

def main():
    n = int(sys.stdin.readline().strip())
    if n == 0:
        print(-1)
        return
    if n % 2 == 1:
        print(1)
        return
    k = 1
    while k <= n:
        if n % k == 0 and (n // k) % 2 == 1:
            print(k)
            return
        k += 1
    print(-1)

if __name__ == "__main__":
    main()
