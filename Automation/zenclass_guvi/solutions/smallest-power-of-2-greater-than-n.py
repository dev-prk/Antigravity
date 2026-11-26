import sys

def main():
    n = int(sys.stdin.readline().strip())
    if n < 0:
        print(1)
    else:
        print(1 << (n).bit_length())

if __name__ == "__main__":
    main()
