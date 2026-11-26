import sys

def main():
    data = sys.stdin.buffer.read().split()
    if not data:
        return
    n = int(data[0])
    if n < 2:
        print(0)
        return
    arr = list(map(int, data[1:1+n]))
    arr.sort()
    min_diff = arr[1] - arr[0]
    for i in range(2, n):
        diff = arr[i] - arr[i-1]
        if diff < min_diff:
            min_diff = diff
    print(min_diff)

if __name__ == "__main__":
    main()
