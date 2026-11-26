import sys

def main():
    n = int(sys.stdin.readline().strip())
    result = 1
    for i in range(1, n + 1):
        result *= i
    print(result)

if __name__ == "__main__":
    main()
