import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    m = int(data[1])
    print(n * m)

if __name__ == "__main__":
    main()
