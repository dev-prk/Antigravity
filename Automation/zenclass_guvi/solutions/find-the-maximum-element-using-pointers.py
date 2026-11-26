import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    if n <= 0:
        return
    arr = list(map(int, data[1:1+n]))
    print(max(arr))

if __name__ == "__main__":
    main()
