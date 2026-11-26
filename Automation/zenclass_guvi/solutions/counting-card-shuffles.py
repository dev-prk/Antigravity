import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        return
    n = int(line)
    result = 1
    for i in range(1, n + 1):
        result *= i
    print(result)

if __name__ == "__main__":
    main()
