import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    arr = list(map(int, data[1:1 + n]))
    if arr:
        print(max(arr))

if __name__ == "__main__":
    main()
