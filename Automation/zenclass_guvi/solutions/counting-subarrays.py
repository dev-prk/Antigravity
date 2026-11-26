import sys

def main():
    data = sys.stdin.buffer.read().split()
    if not data:
        print(0)
        return
    n = int(data[0])
    print(n * (n + 1) // 2)

if __name__ == "__main__":
    main()
