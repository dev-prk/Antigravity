import sys

def main():
    n = int(sys.stdin.readline().strip())
    terms = []
    k = 1
    while True:
        num = 2 * k - 1
        if num > n:
            break
        fact = 1
        for i in range(1, num + 1):
            fact *= i
        terms.append(str(fact))
        k += 1
    print(' '.join(terms))

if __name__ == "__main__":
    main()
