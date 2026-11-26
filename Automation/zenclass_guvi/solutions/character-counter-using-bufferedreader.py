import sys

def main():
    line = sys.stdin.readline()
    count = sum(1 for c in line if not c.isspace())
    print(count)

if __name__ == "__main__":
    main()
