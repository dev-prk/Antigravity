import sys

def main():
    n = int(sys.stdin.readline().strip())
    total = n * (n + 1) // 2
    m = n // 3
    multiples_of_3 = 3 * m * (m + 1) // 2
    result = total - multiples_of_3
    print(result)

if __name__ == "__main__":
    main()
