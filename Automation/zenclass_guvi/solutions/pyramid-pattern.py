import sys

def main():
    n = int(sys.stdin.readline().strip())
    for i in range(n):
        stars = 2 * i + 1
        leading_spaces = 2 * (n - 1 - i)
        if i == 0:
            line = ' ' * leading_spaces + '*'
        else:
            line = ' ' * leading_spaces + ' '.join(['*'] * stars)
        print(line)

if __name__ == "__main__":
    main()
