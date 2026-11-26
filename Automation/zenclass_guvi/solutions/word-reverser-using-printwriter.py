import sys

def main():
    line = sys.stdin.readline()
    if line.endswith('\n'):
        line = line[:-1]
    reversed_str = line[::-1]
    print(reversed_str)

if __name__ == "__main__":
    main()
