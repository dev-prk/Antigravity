import sys

def main() -> None:
    data = sys.stdin.read().strip()
    if not data:
        return
    n = int(data.split()[0])
    if n % 2 == 1:
        print(n - 1)
    else:
        print((n - 2) // 2)

if __name__ == "__main__":
    main()
