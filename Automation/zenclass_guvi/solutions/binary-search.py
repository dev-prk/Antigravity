import sys

def binary_search(arr, key):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == key:
            return mid
        elif arr[mid] < key:
            left = mid + 1
        else:
            right = mid - 1
    return -1

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    idx = 0
    n = int(data[idx])
    idx += 1
    arr = list(map(int, data[idx:idx + n]))
    idx += n
    key = int(data[idx])
    result = binary_search(arr, key)
    if result != -1:
        print(f"Element Found at Index: {result}")
    else:
        print(-1)

if __name__ == "__main__":
    main()
