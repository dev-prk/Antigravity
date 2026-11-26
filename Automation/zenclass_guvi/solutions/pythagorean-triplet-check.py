import sys

def check_triplet(arr, n):
    if n < 3:
        return False
    squares = [x * x for x in arr]
    squares.sort()
    for i in range(n - 1, 1, -1):
        target = squares[i]
        left = 0
        right = i - 1
        while left < right:
            current_sum = squares[left] + squares[right]
            if current_sum == target:
                return True
            elif current_sum < target:
                left += 1
            else:
                right -= 1
    return False

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    idx = 0
    t = int(data[idx])
    idx += 1
    results = []
    for _ in range(t):
        n = int(data[idx])
        idx += 1
        arr = []
        for _ in range(n):
            arr.append(int(data[idx]))
            idx += 1
        if check_triplet(arr, n):
            results.append("Yes")
        else:
            results.append("No")
    for result in results:
        print(result)

if __name__ == "__main__":
    main()
