import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        print(1)
    else:
        print(n.bit_length())

if __name__ == "__main__":
    main()
