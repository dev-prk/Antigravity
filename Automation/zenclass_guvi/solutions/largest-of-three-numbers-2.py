import sys

def main():
    data = sys.stdin.read().split()
    a, b, c = map(int, data[:3])
    print(max(a, b, c))

if __name__ == "__main__":
    main()
