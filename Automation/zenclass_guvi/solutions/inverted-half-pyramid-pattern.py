import sys

def main():
    R = int(sys.stdin.readline().strip())
    for i in range(R, 0, -1):
        print('  '.join(['*'] * i))

if __name__ == "__main__":
    main()
