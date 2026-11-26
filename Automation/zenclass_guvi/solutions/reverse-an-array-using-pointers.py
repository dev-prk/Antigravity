import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    arr = list(map(int, data[1:1+n]))
    left, right = 0, n - 1
    while left < right:
        arr[left], arr[right] = arr[right], arr[left]
        left += 1
        right -= 1
    print(' '.join(map(str, arr)))

if __name__ == "__main__":
    main()
