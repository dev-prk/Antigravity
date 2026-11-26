import sys

def main():
    line = sys.stdin.readline()
    n = int(line.strip())
    multiples = [n * i for i in range(1, 4)]
    print(' '.join(map(str, multiples)))

if __name__ == "__main__":
    main()
