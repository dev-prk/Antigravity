import sys

def main():
    data = sys.stdin.read().strip().splitlines()
    if not data:
        return
    n = int(data[0].strip())
    if n <= 0:
        print(0)
    else:
        print(n * (n + 1) // 2)

if __name__ == "__main__":
    main()
