import sys

def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    idx = 0
    n = int(data[idx])
    idx += 1
    arr = list(map(int, data[idx:idx + n]))
    idx += n
    target = int(data[idx])
    result = binary_search(arr, target)
    print(result)

if __name__ == "__main__":
    main()
