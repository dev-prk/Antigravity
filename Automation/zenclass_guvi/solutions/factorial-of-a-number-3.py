import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    n = int(data)
    result = 1
    for i in range(2, n + 1):
        result *= i
    print(result)

if __name__ == "__main__":
    main()
