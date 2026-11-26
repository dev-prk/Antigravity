import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    print(0 if n <= 1 else n - 1)

if __name__ == "__main__":
    main()
