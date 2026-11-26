import sys

def main():
    data = sys.stdin.read().split()
    if len(data) < 2:
        return
    n = int(data[0])
    k = int(data[1])
    arr = list(map(int, data[2:2 + n]))
    count = arr.count(k)
    if count == 0:
        print(-1)
    else:
        print(count)

if __name__ == "__main__":
    main()
