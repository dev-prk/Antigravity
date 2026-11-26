import sys

def quicksort(arr, low, high):
    if low < high:
        pi = partition(arr, low, high)
        quicksort(arr, low, pi - 1)
        quicksort(arr, pi + 1, high)

def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        print()
        return
    arr = list(map(int, data[1:n+1]))
    if len(arr) > 0:
        quicksort(arr, 0, len(arr) - 1)
    print(' '.join(map(str, arr)))

if __name__ == "__main__":
    main()
