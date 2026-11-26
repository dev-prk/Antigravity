import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        return
    print(line.upper())
    print(len(line))
    print(line[0])
    print(line[-1])

if __name__ == "__main__":
    main()
