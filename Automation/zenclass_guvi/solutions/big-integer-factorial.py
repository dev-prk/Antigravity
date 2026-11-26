import sys

def main():
    n = int(sys.stdin.readline().strip())
    if n == 0 or n == 1:
        print(1)
        return
    result = 1
    for i in range(2, n + 1):
        result *= i
    print(result)

if __name__ == "__main__":
    main()
