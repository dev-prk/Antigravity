import sys

def main():
    data = sys.stdin.buffer.read().split()
    if not data:
        print(0)
        return
    n = int(data[0])
    arr = set(map(int, data[1:1 + n]))
    print(n - len(arr))

if __name__ == "__main__":
    main()
