import sys

def main():
    R = int(sys.stdin.readline().strip())
    for i in range(R):
        if i < R - 1:
            print(' ' * i + '*')
        else:
            print('*' * R)
    for i in range(R - 2, -1, -1):
        print(' ' * i + '*')

if __name__ == "__main__":
    main()
