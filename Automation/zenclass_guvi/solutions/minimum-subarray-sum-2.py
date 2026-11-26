import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        print(0)
        return
    arr = list(map(int, data[1:1+n]))
    cur = best = arr[0]
    for x in arr[1:]:
        cur = min(x, cur + x)
        if cur < best:
            best = cur
    print(best)

if __name__ == "__main__":
    main()
