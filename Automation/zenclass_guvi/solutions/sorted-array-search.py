import sys

def binary_search(arr, k):
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == k:
            return True
        elif arr[mid] < k:
            low = mid + 1
        else:
            high = mid - 1
    return False

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    k = int(data[1])
    arr = list(map(int, data[2:2+n]))
    ans = binary_search(arr, k)
    print('yes' if ans else 'no')

if __name__ == "__main__":
    main()
