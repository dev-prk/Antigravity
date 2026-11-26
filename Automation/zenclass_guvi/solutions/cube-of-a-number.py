import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    print(n ** 3)

if __name__ == "__main__":
    main()
