import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    n = int(data)
    if n == 1:
        print(1)
        return
    a, b = 1, 2
    for _ in range(3, n + 1):
        a, b = b, a + b
    print(b)

if __name__ == "__main__":
    main()
