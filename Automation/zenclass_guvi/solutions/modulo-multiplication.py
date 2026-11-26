import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    a, b, c = map(int, data[:3])
    result = (a * b) % c
    print(result)

if __name__ == "__main__":
    main()
