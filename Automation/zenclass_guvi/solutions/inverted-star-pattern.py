import sys

def main():
    R = int(sys.stdin.readline())
    for i in range(R):
        b = R - i - 1
        stars = 2 * i + 1
        print('b' * b + '*' * stars + 'b' * b)

if __name__ == "__main__":
    main()
