import sys

def main():
    n = int(sys.stdin.readline().strip())
    count = bin(n).count('1')
    print(count)

if __name__ == "__main__":
    main()
