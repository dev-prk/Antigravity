import sys

def main():
    line = sys.stdin.readline()
    n = int(line.strip())
    if n > 0 and (n & (n - 1)) == 0:
        print('yes')
    else:
        print('no')

if __name__ == "__main__":
    main()
