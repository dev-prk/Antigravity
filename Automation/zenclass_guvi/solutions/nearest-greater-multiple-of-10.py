import sys

def main():
    line = sys.stdin.readline()
    if not line:
        return
    n = int(line.strip())
    result = ((n // 10) + 1) * 10
    print(result)

if __name__ == "__main__":
    main()
