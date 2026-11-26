import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        print(-1)
        return
    arr = list(map(int, data[1:n+1]))
    if len(arr) == 0:
        print(-1)
        return
    arr.sort()
    for i in range(len(arr) - 2):
        if arr[i] == arr[i+1] and arr[i+1] == arr[i+2]:
            arr[i] = None
            arr[i+1] = None
            arr[i+2] = None
    for i in range(len(arr)):
        if arr[i] is not None:
            if i + 1 < len(arr) and arr[i+1] == arr[i]:
                print(arr[i])
                return
    print(-1)

if __name__ == "__main__":
    main()
