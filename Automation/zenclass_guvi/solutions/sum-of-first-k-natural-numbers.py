import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    k = int(data[0])
    result = k * (k + 1) // 2
    print(result)

if __name__ == "__main__":
    main()
