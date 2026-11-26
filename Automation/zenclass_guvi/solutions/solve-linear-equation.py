import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    a, b, x = map(int, data[:3])
    y = a * x + b
    print(y)

if __name__ == "__main__":
    main()
