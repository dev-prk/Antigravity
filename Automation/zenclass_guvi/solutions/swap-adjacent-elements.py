import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    arr = list(map(int, data[1:1+n]))
    res = []
    for i in range(0, n, 2):
        if i + 1 < n:
            res.append(str(arr[i+1]))
            res.append(str(arr[i]))
        else:
            res.append(str(arr[i]))
    print(' '.join(res))

if __name__ == "__main__":
    main()
