import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    x = int(data)
    print(1 + 9 * x)

if __name__ == "__main__":
    main()
