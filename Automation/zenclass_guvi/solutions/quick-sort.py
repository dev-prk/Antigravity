def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

def main():
    import sys
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        print(-1)
        return
    arr = list(map(int, data[1:n+1]))
    if not all(-10**9 <= x <= 10**9 for x in arr):
        print(-1)
        return
    sorted_arr = quick_sort(arr)
    print(' '.join(map(str, sorted_arr)))

if __name__ == "__main__":
    main()
